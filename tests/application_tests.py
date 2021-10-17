import unittest

import application.GameInstance
from application.Riddle import Riddle, RiddleManager
from application.JsonLoader import ConfigLoader
from application.GameInstance import GameInstanceManager, GameInstanceException


class RiddleTests(unittest.TestCase):

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
            self.COMPLETION_IMAGE_NAME
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


class RiddleManagerTests(unittest.TestCase):

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
            self.COMPLETION_IMAGE_NAME
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


class JsonLoaderTests(unittest.TestCase):
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
        self.assertEqual(self.json_config_loader.get_config_file_name(), self.CONFIG_NAME)

    def test_get_riddles_type(self):
        self.assertEqual(type(self.json_config_loader.get_riddles()), type(dict()))

    def test_get_riddles_count(self):
        self.assertEqual(len(self.json_config_loader.get_riddles()), 3)


class GameInstanceManageTests(unittest.TestCase):
    DUMMY_GAME = "DUMMY_GAME"
    MAX_GAMES = 1

    def setUp(self):
        self.game_instance_manager = GameInstanceManager(1)

    def test_get_game_key_set(self):
        self.assertIsNotNone(self.game_instance_manager.get_game_key_set())

    def test_add_game(self):
        game_key, admin_key = self.game_instance_manager.get_game_key_set()
        self.game_instance_manager.set_game_instance(game_key, admin_key, self.DUMMY_GAME)
        self.assertEqual(self.game_instance_manager.get_game_by_game_key(game_key), self.DUMMY_GAME)

    def test_get_game_by_admin_key(self):
        game_key, admin_key = self.game_instance_manager.get_game_key_set()
        self.game_instance_manager.set_game_instance(game_key, admin_key, self.DUMMY_GAME)
        self.assertEqual(self.game_instance_manager.get_game_by_admin_key(admin_key), self.DUMMY_GAME)

    def test_get_game_key_by_admin_key(self):
        game_key, admin_key = self.game_instance_manager.get_game_key_set()
        self.game_instance_manager.set_game_instance(game_key, admin_key, self.DUMMY_GAME)
        self.assertEqual(self.game_instance_manager.get_game_key_by_admin_key(admin_key), game_key)




