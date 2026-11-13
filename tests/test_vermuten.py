import unittest
from unittest.mock import MagicMock, patch
from app import app
from application.Riddle import Riddle, RiddleManager
from application.JsonLoader import ConfigLoader


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
        response = self.app.get("/restart")
        self.assertEqual(response.status_code, 302)
        mock_riddle_manager.reset_progress.assert_called_once()

    @patch("app.riddle_manager")
    def test_reset_admin_page_route(self, mock_riddle_manager):
        response = self.app.get("/admin/reset")
        self.assertEqual(response.status_code, 302)
        mock_riddle_manager.reset_progress.assert_called_once()

    @patch("app.riddle_manager")
    def test_progress_route(self, mock_riddle_manager):
        mock_riddle_manager.get_current_riddle_number.return_value = 1
        mock_riddle_manager.get_riddle_count.return_value = 10
        mock_riddle_manager.get_current_riddle.return_value = self.riddle
        mock_riddle_manager.get_total_attempt_count.return_value = 5
        response = self.app.get("/admin/progress")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Riddle Progress: 1 of 10", response.data)
        self.assertIn(b"Current riddle: riddle", response.data)
        self.assertIn(b"Total number of attempts: 5", response.data)
