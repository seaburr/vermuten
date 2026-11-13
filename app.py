import os
import logging
import uuid
from flask import Flask
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from flask import jsonify
from application.JsonLoader import ConfigLoader

logging_format = (
    "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s"
)
logging.basicConfig(level=logging.INFO, format=logging_format)

app = Flask(__name__)

config_file = os.environ.get("VERMUTEN_CONFIG")
if config_file:
    logging.info("Loading config from file...")
    config_loader = ConfigLoader(config_file)
    riddle_manager = config_loader.get_riddle_manager()

game_sessions = {}

def get_riddle_manager(game_id=None):
    if game_id:
        return game_sessions.get(game_id)
    return riddle_manager


@app.route("/")
def index():
    if "riddle_manager" in globals():
        return redirect(url_for("riddle"))
    return render_template("setup.html.j2")


@app.route("/setup", methods=["POST"])
def setup():
    if "file" not in request.files:
        return "No file part", 400
    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400
    if file:
        game_id = str(uuid.uuid4())
        # It's better to save the file to a temporary directory
        # but for simplicity, we'll hold it in memory.
        config_loader = ConfigLoader(file)
        riddle_manager = config_loader.get_riddle_manager()
        game_sessions[game_id] = riddle_manager
        return jsonify({"game_url": url_for("riddle", game_id=game_id)})


@app.route("/riddle/", defaults={"game_id": None})
@app.route("/riddle/<game_id>/")
def riddle(game_id):
    riddle_manager = get_riddle_manager(game_id)
    if not riddle_manager:
        return "Game not found", 404

    guess = request.args.get("guess")
    current_riddle = riddle_manager.get_current_riddle()
    riddle_id = riddle_manager.get_current_riddle_number()
    if guess is None and current_riddle is not None:
        return render_template(
            "index.html.j2",
            game_id=game_id,
            riddle_id=riddle_id,
            riddle=current_riddle.get_riddle(),
            image_name=current_riddle.get_image_name(),
            hint=current_riddle.get_hint(),
        )
    elif guess is not None and current_riddle is not None:
        if current_riddle.test_answer(guess):
            riddle_manager.next_riddle()
            return redirect(url_for("riddle", game_id=game_id))
        else:
            return render_template(
                "index.html.j2",
                game_id=game_id,
                riddle_id=riddle_id,
                riddle=current_riddle.get_riddle(),
                image_name=current_riddle.get_image_name(),
                hint=current_riddle.get_hint(),
                response=current_riddle.get_random_incorrect_response(),
            )
    else:
        logging.info(riddle_manager.get_current_riddle())
        return render_template(
            "complete.html.j2",
            game_id=game_id,
            completion_message=riddle_manager.get_completion_message(),
            image_name=riddle_manager.get_completion_image_name(),
            attempts=riddle_manager.get_total_attempt_count(),
        )


@app.route("/riddle/data", defaults={"game_id": None})
@app.route("/riddle/<game_id>/data")
def api_data(game_id):
    riddle_manager = get_riddle_manager(game_id)
    if not riddle_manager:
        return "Game not found", 404

    current_riddle = riddle_manager.get_current_riddle()
    if current_riddle is None:
        game_over = True
        return jsonify(game_over=game_over)
    else:
        riddle = current_riddle.get_riddle()
        image_name = current_riddle.get_image_name()
        riddle_id = riddle_manager.get_current_riddle_number()
        hint = current_riddle.get_hint()
        return jsonify(
            riddle_id=f"Riddle #{riddle_id}",
            riddle=riddle,
            image_name=f"/static/{image_name}",
            hint=f"Hint: {hint}",
        )


@app.route("/riddle/restart", defaults={"game_id": None})
@app.route("/riddle/<game_id>/restart")
def reset(game_id):
    riddle_manager = get_riddle_manager(game_id)
    if not riddle_manager:
        return "Game not found", 404

    current_riddle = riddle_manager.get_current_riddle()
    if current_riddle is None:
        riddle_manager.reset_progress()
    return redirect(url_for("riddle", game_id=game_id))


@app.route("/riddle/admin/reset", defaults={"game_id": None})
@app.route("/riddle/<game_id>/admin/reset")
def reset_admin_page(game_id):
    riddle_manager = get_riddle_manager(game_id)
    if not riddle_manager:
        return "Game not found", 404

    riddle_manager.reset_progress()
    return redirect(url_for("progress", game_id=game_id))


@app.route("/riddle/admin/progress", defaults={"game_id": None})
@app.route("/riddle/<game_id>/admin/progress")
def progress(game_id):
    riddle_manager = get_riddle_manager(game_id)
    if not riddle_manager:
        return "Game not found", 404

    return render_template(
        "progress.html.j2",
        game_id=game_id,
        current_riddle_number=riddle_manager.get_current_riddle_number(),
        riddle_count=riddle_manager.get_riddle_count(),
        current_riddle=riddle_manager.get_current_riddle().get_riddle(),
        attempts=riddle_manager.get_total_attempt_count(),
    )


if __name__ == "__main__":
    logging.info("Starting vermuten...")
    app.run()
