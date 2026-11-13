import json
import logging
from application.Riddle import Riddle, RiddleManager


class ConfigLoadException(Exception):
    pass


class ConfigLoader(object):
    def __init__(self, json_config_file):
        self.json_config_file = json_config_file
        self.riddle_collection = dict()
        self._load_config()

    def _load_config(self):
        try:
            logging.info(f"Loading config from file.")
            with open(self.json_config_file, "r") as f:
                json_config = json.loads(f.read())
            logging.debug(f"Config:\n{json_config}")
            incorrect_responses = json_config["incorrect_responses"]
            correct_responses = json_config["correct_responses"]
            completion_message = json_config["completion_message"]
            completion_image_name = json_config["completion_image_name"]
            for riddle in json_config["riddles"]:
                logging.debug(f"Creating riddle object for {riddle}.")
                riddle_object = Riddle(
                    riddle["question"],
                    riddle["answer"],
                    riddle["hint"],
                    riddle["image_name"],
                    correct_responses,
                    incorrect_responses,
                    completion_message,
                    completion_image_name,
                )
                self.riddle_collection[len(self.riddle_collection)] = riddle_object
            logging.info(f"Successfully loaded config.")
            logging.info(f"Riddle count: {len(self.riddle_collection)}")
            logging.info(f"Incorrect response count: {len(incorrect_responses)}")
            logging.info(f"Correct response count: {len(correct_responses)}")
        except Exception as err:
            logging.error(f"{err}")
            raise ConfigLoadException

    def get_riddles(self):
        return self.riddle_collection

    def get_riddle_manager(self):
        riddle_manager = RiddleManager(self.get_riddles())
        return riddle_manager

    def get_config_file_name(self):
        return self.json_config_file
