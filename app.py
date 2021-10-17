import os
import logging
from flask import Flask
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from application.JsonLoader import ConfigLoader
from application.GameInstance import GameInstanceManager

logging_format = (
    "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s"
)
logging.basicConfig(level=logging.INFO, format=logging_format)

app = Flask(__name__)
config_file = os.getenv("VERMUTEN_CONFIG")
game_instances = GameInstanceManager(5)


@app.route("/")
def riddle():
    return "Not implemented. Go go /new to create a new game!"


@app.route("/new")
def new_game():
    game_key = game_instances.get_new_game_key()
    config_loader = ConfigLoader(config_file)
    game = config_loader.get_riddle_manager()
    game_instances.set_game_instance(game_key, game)
    return f"Game key is <b>{game_key}</b>. Go to /play/{game_key} to begin."


@app.route("/play/<game_key>")
def play(game_key):
    guess = request.args.get("guess")
    riddle_manager = game_instances.get_game(game_key)
    current_riddle = riddle_manager.get_current_riddle()
    riddle_id = riddle_manager.get_current_riddle_number()
    if guess is None and current_riddle is not None:
        return render_template(
            "index.html.j2",
            game_key=game_key,
            riddle_id=riddle_id,
            riddle=current_riddle.get_riddle(),
            image_name=current_riddle.get_image_name(),
            hint=current_riddle.get_hint(),
        )
    elif guess is not None and current_riddle is not None:
        if current_riddle.test_answer(guess):
            riddle_manager.next_riddle()
            return redirect(url_for("play", game_key=game_key))
        else:
            return render_template(
                "index.html.j2",
                game_key=game_key,
                riddle_id=riddle_id,
                riddle=current_riddle.get_riddle(),
                image_name=current_riddle.get_image_name(),
                hint=current_riddle.get_hint(),
                response=current_riddle.get_random_incorrect_response(),
            )
    else:
        return render_template(
            "complete.html.j2",
            game_key=game_key,
            completion_message=riddle_manager.get_completion_message(),
            image_name=riddle_manager.get_completion_image_name(),
            attempts=riddle_manager.get_total_attempt_count(),
        )


@app.route("/<game_key>/restart")
def reset(game_key):
    riddle_manager = game_instances.get_game(game_key)
    riddle_manager.reset_progress()
    return redirect(url_for("play", game_key=game_key))


@app.route("/admin/<game_key>/reset")
def reset_admin_page(game_key):
    riddle_manager = game_instances.get_game(game_key)
    riddle_manager.reset_progress()
    return redirect(url_for("progress", game_key=game_key))


@app.route("/admin/<game_key>")
def progress(game_key):
    riddle_manager = game_instances.get_game(game_key)
    return render_template(
        "progress.html.j2",
        game_key=game_key,
        current_riddle_number=riddle_manager.get_current_riddle_number(),
        riddle_count=riddle_manager.get_riddle_count(),
        current_riddle=riddle_manager.get_current_riddle().get_riddle(),
        attempts=riddle_manager.get_total_attempt_count()
    )


if __name__ == "__main__":
    logging.info("Starting vermuten...")
    app.run()

