import unittest
import io
import json
from unittest.mock import patch
from app import app
from application.Riddle import Riddle, RiddleManager
from application.JsonLoader import ConfigLoader, ConfigLoadException


class TestRiddle(unittest.TestCase):

    RIDDLE = "riddle"
    ANSWER = ["answer"]
    CORRECT_ANSWER = "answer"
    INCORRECT_ANSWER = "not answer"
    HINT = "HINT"
    IMAGE_NAME = "image_name.jpg"
    CORRECT_RESPONSES = ["yes"]
    INCORRECT_RESPONSES = ["no"]
    COMPLETION_MESSAGE = "done"
    COMPLETION_IMAGE_NAME = "all_done.png"

    def setUp(self):
        self.riddle = Riddle(
            self.RIDDLE,
            self.ANSWER,
            self.HINT,
            self.IMAGE_NAME,
            self.CORRECT_RESPONSES,
            self.INCORRECT_RESPONSES,
            self.COMPLETION_MESSAGE,
            self.COMPLETION_IMAGE_NAME,
        )

    def test_get_riddle(self):
        self.assertEqual(self.riddle.get_riddle(), self.RIDDLE)

    def test_correct_answer(self):
        self.assertTrue(self.riddle.test_answer(self.CORRECT_ANSWER))

    def test_incorrect_answer(self):
        self.assertFalse(self.riddle.test_answer(self.INCORRECT_ANSWER))

    def test_attempt_counter(self):
        self.riddle.test_answer(self.CORRECT_ANSWER)
        self.riddle.test_answer(self.INCORRECT_ANSWER)
        self.assertEqual(self.riddle.get_attempts(), 2)
        self.riddle.reset_attempts()
        self.assertEqual(self.riddle.get_attempts(), 0)

    def test_get_hint(self):
        self.assertEqual(self.riddle.get_hint(), self.HINT)

    def test_get_image_name(self):
        self.assertEqual(self.riddle.get_image_name(), self.IMAGE_NAME)

    def test_get_correct_response(self):
        self.assertIn(self.riddle.get_random_correct_response(), self.CORRECT_RESPONSES)

    def test_get_incorrect_response(self):
        self.assertIn(
            self.riddle.get_random_incorrect_response(), self.INCORRECT_RESPONSES
        )

    def test_get_completion_message(self):
        self.assertEqual(self.riddle.get_completion_message(), self.COMPLETION_MESSAGE)


class TestRiddleManager(unittest.TestCase):

    RIDDLE = "riddle"
    ANSWER = ["answer"]
    CORRECT_ANSWER = "answer"
    INCORRECT_ANSWER = "not answer"
    HINT = "HINT"
    IMAGE_NAME = "image_name.jpg"
    CORRECT_RESPONSES = ["yes"]
    INCORRECT_RESPONSES = ["no"]
    COMPLETION_MESSAGE = "done"
    COMPLETION_IMAGE_NAME = "all_done.png"

    def setUp(self):
        self.riddle = Riddle(
            self.RIDDLE,
            self.ANSWER,
            self.HINT,
            self.IMAGE_NAME,
            self.CORRECT_RESPONSES,
            self.INCORRECT_RESPONSES,
            self.COMPLETION_MESSAGE,
            self.COMPLETION_IMAGE_NAME,
        )
        self.riddle_collection = {0: self.riddle}
        self.riddle_manager = RiddleManager(self.riddle_collection)

    def test_get_current_riddle(self):
        self.assertEqual(self.riddle_manager.get_current_riddle(), self.riddle)

    def test_no_more_riddles(self):
        self.riddle_manager.next_riddle()
        self.assertEqual(self.riddle_manager.get_current_riddle(), None)

    def test_reset_progress(self):
        self.riddle_manager.next_riddle()
        self.assertEqual(self.riddle_manager.get_current_riddle_number(), 2)
        self.riddle_manager.reset_progress()
        self.assertEqual(self.riddle_manager.get_current_riddle_number(), 1)

    def test_get_total_attempt_count(self):
        riddle = self.riddle_manager.get_current_riddle()
        self.assertEqual(self.riddle_manager.get_total_attempt_count(), 0)
        riddle.test_answer(self.CORRECT_ANSWER)
        riddle.test_answer(self.INCORRECT_ANSWER)
        self.assertEqual(self.riddle_manager.get_total_attempt_count(), 2)

    def test_get_completion_message(self):
        self.assertEqual(
            self.riddle_manager.get_completion_message(), self.COMPLETION_MESSAGE
        )

    def test_get_completion_image_name(self):
        self.assertEqual(
            self.riddle_manager.get_completion_image_name(), self.COMPLETION_IMAGE_NAME
        )

    def test_get_riddle_count(self):
        self.assertEqual(self.riddle_manager.get_riddle_count(), 1)


class TestJsonLoader(unittest.TestCase):
    CONFIG_FILE_NAME = "./tests/test_config.json"
    CONFIG_NAME = "test_config"

    def setUp(self):
        self.json_config_loader = ConfigLoader(self.CONFIG_FILE_NAME)

    def test_config_load(self):
        self.assertIsNotNone(self.json_config_loader)

    def test_get_riddle_manager(self):
        riddle_manager = self.json_config_loader.get_riddle_manager()
        self.assertEqual(type(riddle_manager), RiddleManager)

    def test_get_config_file_name(self):
        self.assertEqual(
            self.json_config_loader.get_config_file_name(), self.CONFIG_NAME
        )

    def test_get_riddles_type(self):
        self.assertEqual(type(self.json_config_loader.get_riddles()), type(dict()))

    def test_get_riddles_count(self):
        self.assertEqual(len(self.json_config_loader.get_riddles()), 3)


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.riddle = Riddle(
            "riddle",
            ["answer"],
            "hint",
            "image_name.jpg",
            ["correct"],
            ["incorrect"],
            "completion_message",
            "completion_image_name.jpg",
        )

    @patch("app.riddle_manager")
    def test_riddle_route_no_guess(self, mock_riddle_manager):
        mock_riddle_manager.get_current_riddle.return_value = self.riddle
        mock_riddle_manager.get_current_riddle_number.return_value = 1
        response = self.app.get("/riddle/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"riddle", response.data)

    @patch("app.riddle_manager")
    def test_riddle_route_correct_guess(self, mock_riddle_manager):
        mock_riddle_manager.get_current_riddle.return_value = self.riddle
        with patch.object(self.riddle, "test_answer", return_value=True):
            response = self.app.get("/riddle/?guess=answer")
            self.assertEqual(response.status_code, 302)

    @patch("app.riddle_manager")
    def test_riddle_route_incorrect_guess(self, mock_riddle_manager):
        mock_riddle_manager.get_current_riddle.return_value = self.riddle
        with patch.object(self.riddle, "test_answer", return_value=False):
            response = self.app.get("/riddle/?guess=wrong")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"incorrect", response.data)

    @patch("app.riddle_manager")
    def test_riddle_route_no_more_riddles(self, mock_riddle_manager):
        mock_riddle_manager.get_current_riddle.return_value = None
        mock_riddle_manager.get_completion_message.return_value = "completion_message"
        mock_riddle_manager.get_completion_image_name.return_value = (
            "completion_image_name.jpg"
        )
        mock_riddle_manager.get_total_attempt_count.return_value = 0
        response = self.app.get("/riddle/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"completion_message", response.data)

    @patch("app.riddle_manager")
    def test_data_route(self, mock_riddle_manager):
        mock_riddle_manager.get_current_riddle.return_value = self.riddle
        mock_riddle_manager.get_current_riddle_number.return_value = 1
        response = self.app.get("/riddle/data")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["riddle"], "riddle")

    @patch("app.riddle_manager")
    def test_data_route_no_more_riddles(self, mock_riddle_manager):
        mock_riddle_manager.get_current_riddle.return_value = None
        response = self.app.get("/riddle/data")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data["game_over"])

    @patch("app.riddle_manager")
    def test_reset_route(self, mock_riddle_manager):
        mock_riddle_manager.get_current_riddle.return_value = None
        response = self.app.get("/riddle/restart")
        self.assertEqual(response.status_code, 302)
        mock_riddle_manager.reset_progress.assert_called_once()

    @patch("app.riddle_manager")
    def test_reset_admin_page_route(self, mock_riddle_manager):
        response = self.app.get("/riddle/admin/reset")
        self.assertEqual(response.status_code, 302)
        mock_riddle_manager.reset_progress.assert_called_once()

    @patch("app.riddle_manager")
    def test_progress_route(self, mock_riddle_manager):
        mock_riddle_manager.get_current_riddle_number.return_value = 1
        mock_riddle_manager.get_riddle_count.return_value = 10
        mock_riddle_manager.get_current_riddle.return_value = self.riddle
        mock_riddle_manager.get_total_attempt_count.return_value = 5
        response = self.app.get("/riddle/admin/progress")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Riddle Progress: 1 of 10", response.data)
        self.assertIn(b"Current riddle: riddle", response.data)
        self.assertIn(b"Total number of attempts: 5", response.data)


def load_demo_config():
    with open("demo.json", encoding="utf-8") as f:
        return json.load(f)


class TestConfigFromStream(unittest.TestCase):
    def test_load_from_stream(self):
        data = json.dumps(load_demo_config()).encode()
        loader = ConfigLoader(stream=io.BytesIO(data), name="my_game.json")
        self.assertEqual(len(loader.get_riddles()), 3)
        self.assertEqual(loader.get_config_file_name(), "my_game")

    def test_answers_are_normalised(self):
        config = load_demo_config()
        config["riddles"][0]["answer"] = ["  EGG "]
        loader = ConfigLoader(stream=io.BytesIO(json.dumps(config).encode()))
        self.assertTrue(loader.get_riddles()[0].test_answer("Egg"))

    def test_bad_json(self):
        with self.assertRaises(ConfigLoadException):
            ConfigLoader(stream=io.BytesIO(b"{not json"))

    def test_bad_shape(self):
        config = load_demo_config()
        config["riddles"][1]["answer"] = "candle"
        with self.assertRaises(ConfigLoadException) as ctx:
            ConfigLoader(stream=io.BytesIO(json.dumps(config).encode()))
        self.assertIn("Riddle 2", str(ctx.exception))


class TestSetupAndHealth(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def upload(self, data, filename="game.json"):
        return self.app.post(
            "/setup",
            data={"file": (io.BytesIO(data), filename)},
            content_type="multipart/form-data",
        )

    def test_healthz(self):
        response = self.app.get("/healthz")
        self.assertEqual(response.status_code, 200)

    @patch("app.riddle_manager", None)
    def test_index_shows_setup_without_config(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Upload a game file", response.data)

    def test_upload_and_play(self):
        response = self.upload(json.dumps(load_demo_config()).encode())
        self.assertEqual(response.status_code, 200)
        game_url = response.get_json()["game_url"]
        self.assertTrue(game_url.startswith("/riddle/"))
        page = self.app.get(game_url)
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"What has to be broken", page.data)
        answer = self.app.get(game_url + "?guess=egg")
        self.assertEqual(answer.status_code, 302)
        page = self.app.get(game_url)
        self.assertIn(b"Riddle #2", page.data)

    def test_upload_no_file(self):
        response = self.app.post("/setup", data={})
        self.assertEqual(response.status_code, 400)

    def test_upload_bad_json(self):
        response = self.upload(b"{not json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("not valid JSON", response.get_json()["error"])

    def test_upload_bad_shape(self):
        response = self.upload(json.dumps({"riddles": []}).encode())
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_upload_too_large(self):
        response = self.upload(b" " * (300 * 1024))
        self.assertEqual(response.status_code, 413)
        self.assertIn("error", response.get_json())

    def test_unknown_game(self):
        response = self.app.get("/riddle/not-a-game/")
        self.assertEqual(response.status_code, 404)
