import os
import logging
from flask import Flask
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from application.Riddle import RiddleManager
from application.GameInstance import GameInstanceManager

logging_format = (
    "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s"
)
logging.basicConfig(level=logging.INFO, format=logging_format)

app = Flask(__name__)
config_file = os.getenv("VERMUTEN_CONFIG")
max_games = 50
game_instances = GameInstanceManager(max_games)


@app.route("/")
def riddle():
    game_key, admin_key = game_instances.get_game_key_set()
    game = RiddleManager(None)
    try:
        game_instances.set_game_instance(game_key, admin_key, game)
    except:
        logging.warning("Deleting the oldest game instance.")
        game_instances.delete_oldest_game()
        game_instances.set_game_instance(game_key, admin_key, game)
    play_url = url_for("play", game_key=game_key)
    admin_url = url_for("progress", admin_key=admin_key)
    return render_template("landing.html.j2",
                           game_key=game_key,
                           admin_key=admin_key,
                           play_url=play_url,
                           admin_url=admin_url
                           )


@app.route("/play/<game_key>")
def play(game_key):
    guess = request.args.get("guess")
    riddle_manager = game_instances.get_game_by_game_key(game_key)
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
    riddle_manager = game_instances.get_game_by_game_key(game_key)
    riddle_manager.reset_progress()
    return redirect(url_for("play", game_key=game_key))


@app.route("/admin/<admin_key>/reset")
def reset_admin_page(admin_key):
    riddle_manager = game_instances.get_game_by_admin_key(admin_key)
    riddle_manager.reset_progress()
    return redirect(url_for("progress", admin_key=admin_key))


@app.route("/admin/<admin_key>")
def progress(admin_key):
    riddle_manager = game_instances.get_game_by_admin_key(admin_key)
    game_key = game_instances.get_game_key_by_admin_key(admin_key)
    play_url = url_for("play", game_key=game_key)
    return render_template(
        "progress.html.j2",
        game_key=game_key,
        admin_key=admin_key,
        play_url=play_url,
        current_riddle_number=riddle_manager.get_current_riddle_number(),
        riddle_count=riddle_manager.get_riddle_count(),
        current_riddle=riddle_manager.get_current_riddle().get_riddle(),
        attempts=riddle_manager.get_total_attempt_count()
    )


@app.route("/admin/<admin_key>/add_riddles")
def add_riddles(admin_key):
    riddle_manager = game_instances.get_game_by_admin_key(admin_key)
    new_riddles = dict()
    new_riddles[request.args.get("riddle_1")] = request.args.get("answer_1")
    new_riddles[request.args.get("riddle_2")] = request.args.get("answer_2")
    new_riddles[request.args.get("riddle_3")] = request.args.get("answer_3")
    for question, answer in new_riddles.items():
        if question is not None or question not in ["", " "]:
            logging.info(f"Creating a new riddle: {question}, answer: {answer}")
            riddle_manager.add_basic_riddle(question, answer)
    return redirect(url_for("progress", admin_key=admin_key))


if __name__ == "__main__":
    logging.info("Starting vermuten...")
    app.run()

