import io
import logging
import os
import threading
import uuid
from collections import OrderedDict

from flask import Flask, jsonify, redirect, render_template, request, url_for

from application.JsonLoader import ConfigLoader, ConfigLoadException

logging_format = (
    "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s"
)
logging.basicConfig(level=logging.INFO, format=logging_format)

# Largest config accepted on /setup. The request limit leaves room for the
# multipart envelope around the file.
MAX_CONFIG_BYTES = 256 * 1024
# Uploaded games live in memory; the oldest is dropped past this many.
MAX_GAME_SESSIONS = 100

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONFIG_BYTES + 64 * 1024

# Game state is in memory, so the app runs as ONE process (threads are fine).
state_lock = threading.Lock()
riddle_manager = None
game_sessions = OrderedDict()

config_file = os.environ.get("VERMUTEN_CONFIG")
if config_file:
    logging.info("Loading config from file...")
    riddle_manager = ConfigLoader(config_file).get_riddle_manager()


def get_riddle_manager(game_id=None):
    if game_id:
        return game_sessions.get(game_id)
    return riddle_manager


@app.errorhandler(413)
def too_large(_error):
    limit_kb = MAX_CONFIG_BYTES // 1024
    return jsonify(error=f"The config file is larger than {limit_kb} KB."), 413


@app.route("/healthz")
def healthz():
    return "ok", 200


@app.route("/")
def index():
    if riddle_manager is not None:
        return redirect(url_for("riddle"))
    return render_template("setup.html.j2", max_kb=MAX_CONFIG_BYTES // 1024)


@app.route("/setup", methods=["POST"])
def setup():
    file = request.files.get("file")
    if file is None or file.filename == "":
        return jsonify(error="No file selected."), 400
    data = file.stream.read(MAX_CONFIG_BYTES + 1)
    if len(data) > MAX_CONFIG_BYTES:
        return too_large(None)
    try:
        loader = ConfigLoader(stream=io.BytesIO(data), name=file.filename)
    except ConfigLoadException as err:
        return jsonify(error=str(err)), 400
    game_id = str(uuid.uuid4())
    with state_lock:
        game_sessions[game_id] = loader.get_riddle_manager()
        while len(game_sessions) > MAX_GAME_SESSIONS:
            game_sessions.popitem(last=False)
    return jsonify(game_url=url_for("riddle", game_id=game_id))


def render_riddle(game_id, manager, current_riddle, response=None):
    return render_template(
        "index.html.j2",
        title="Vermuten",
        game_id=game_id,
        riddle_id=manager.get_current_riddle_number(),
        riddle=current_riddle.get_riddle(),
        image_name=current_riddle.get_image_name(),
        hint=current_riddle.get_hint(),
        response=response,
    )


@app.route("/riddle/", defaults={"game_id": None})
@app.route("/riddle/<game_id>/")
def riddle(game_id):
    manager = get_riddle_manager(game_id)
    if not manager:
        return "Game not found", 404

    guess = request.args.get("guess")
    with state_lock:
        current_riddle = manager.get_current_riddle()
        if current_riddle is None:
            return render_template(
                "complete.html.j2",
                game_id=game_id,
                completion_message=manager.get_completion_message(),
                image_name=manager.get_completion_image_name(),
                attempts=manager.get_total_attempt_count(),
            )
        if guess is None:
            return render_riddle(game_id, manager, current_riddle)
        if current_riddle.test_answer(guess.strip()):
            manager.next_riddle()
            return redirect(url_for("riddle", game_id=game_id))
        return render_riddle(
            game_id,
            manager,
            current_riddle,
            response=current_riddle.get_random_incorrect_response(),
        )


@app.route("/riddle/data", defaults={"game_id": None})
@app.route("/riddle/<game_id>/data")
def api_data(game_id):
    manager = get_riddle_manager(game_id)
    if not manager:
        return "Game not found", 404

    current_riddle = manager.get_current_riddle()
    if current_riddle is None:
        return jsonify(game_over=True)
    return jsonify(
        riddle_id=f"Riddle #{manager.get_current_riddle_number()}",
        riddle=current_riddle.get_riddle(),
        image_name=url_for("static", filename=current_riddle.get_image_name()),
        hint=f"Hint: {current_riddle.get_hint()}",
    )


@app.route("/riddle/restart", defaults={"game_id": None})
@app.route("/riddle/<game_id>/restart")
def reset(game_id):
    manager = get_riddle_manager(game_id)
    if not manager:
        return "Game not found", 404

    with state_lock:
        if manager.get_current_riddle() is None:
            manager.reset_progress()
    return redirect(url_for("riddle", game_id=game_id))


@app.route("/riddle/admin/reset", defaults={"game_id": None})
@app.route("/riddle/<game_id>/admin/reset")
def reset_admin_page(game_id):
    manager = get_riddle_manager(game_id)
    if not manager:
        return "Game not found", 404

    with state_lock:
        manager.reset_progress()
    return redirect(url_for("progress", game_id=game_id))


@app.route("/riddle/admin/progress", defaults={"game_id": None})
@app.route("/riddle/<game_id>/admin/progress")
def progress(game_id):
    manager = get_riddle_manager(game_id)
    if not manager:
        return "Game not found", 404

    current_riddle = manager.get_current_riddle()
    return render_template(
        "progress.html.j2",
        game_id=game_id,
        current_riddle_number=min(
            manager.get_current_riddle_number(), manager.get_riddle_count()
        ),
        riddle_count=manager.get_riddle_count(),
        current_riddle=(
            current_riddle.get_riddle()
            if current_riddle is not None
            else "All riddles solved."
        ),
        attempts=manager.get_total_attempt_count(),
    )


if __name__ == "__main__":
    logging.info("Starting vermuten...")
    app.run(port=int(os.environ.get("PORT", "8080")))
