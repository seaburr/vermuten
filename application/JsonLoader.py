import json
import logging
import os
from application.Riddle import Riddle, RiddleManager


class ConfigLoadException(Exception):
    pass


REQUIRED_STRINGS = ("completion_message", "completion_image_name")
REQUIRED_STRING_LISTS = ("incorrect_responses", "correct_responses")
RIDDLE_STRINGS = ("question", "hint", "image_name")


def _is_string_list(value):
    return (
        isinstance(value, list)
        and len(value) > 0
        and all(isinstance(item, str) for item in value)
    )


def validate_config(json_config):
    """Check the shape of a parsed config. Raises ConfigLoadException with a
    message that is safe to show to the person who supplied the config."""
    if not isinstance(json_config, dict):
        raise ConfigLoadException("The config must be a JSON object.")
    for key in REQUIRED_STRINGS:
        if not isinstance(json_config.get(key), str):
            raise ConfigLoadException(f"'{key}' must be a string.")
    for key in REQUIRED_STRING_LISTS:
        if not _is_string_list(json_config.get(key)):
            raise ConfigLoadException(f"'{key}' must be a non-empty list of strings.")
    riddles = json_config.get("riddles")
    if not isinstance(riddles, list) or len(riddles) == 0:
        raise ConfigLoadException("'riddles' must be a non-empty list.")
    for number, riddle in enumerate(riddles, start=1):
        if not isinstance(riddle, dict):
            raise ConfigLoadException(f"Riddle {number} must be a JSON object.")
        for key in RIDDLE_STRINGS:
            if not isinstance(riddle.get(key), str):
                raise ConfigLoadException(f"Riddle {number}: '{key}' must be a string.")
        if not _is_string_list(riddle.get("answer")):
            raise ConfigLoadException(
                f"Riddle {number}: 'answer' must be a non-empty list of strings."
            )


class ConfigLoader(object):
    """Loads a riddle config from a file path, or from an already open
    binary/text stream (for example an uploaded file's stream)."""

    def __init__(self, json_config_file=None, stream=None, name=None):
        if (json_config_file is None) == (stream is None):
            raise ValueError("Pass exactly one of json_config_file or stream.")
        self.json_config_file = json_config_file
        self.stream = stream
        self.name = name
        self.riddle_collection = dict()
        self._load_config()

    def _read(self):
        if self.stream is not None:
            return self.stream.read()
        with open(self.json_config_file, "r", encoding="utf-8") as f:
            return f.read()

    def _load_config(self):
        try:
            json_config = json.loads(self._read())
        except (OSError, UnicodeDecodeError, ValueError) as err:
            logging.error(f"Could not read config: {err}")
            raise ConfigLoadException("The config is not valid JSON.") from err
        validate_config(json_config)
        incorrect_responses = json_config["incorrect_responses"]
        correct_responses = json_config["correct_responses"]
        completion_message = json_config["completion_message"]
        completion_image_name = json_config["completion_image_name"]
        for riddle in json_config["riddles"]:
            riddle_object = Riddle(
                riddle["question"],
                [answer.strip().lower() for answer in riddle["answer"]],
                riddle["hint"],
                riddle["image_name"],
                correct_responses,
                incorrect_responses,
                completion_message,
                completion_image_name,
            )
            self.riddle_collection[len(self.riddle_collection)] = riddle_object
        logging.info("Successfully loaded config.")
        logging.info(f"Riddle count: {len(self.riddle_collection)}")
        logging.info(f"Incorrect response count: {len(incorrect_responses)}")
        logging.info(f"Correct response count: {len(correct_responses)}")

    def get_riddles(self):
        return self.riddle_collection

    def get_riddle_manager(self):
        return RiddleManager(self.get_riddles())

    def get_config_file_name(self):
        """The config's name without directory or extension."""
        source = self.json_config_file or self.name
        if not source:
            return None
        return os.path.splitext(os.path.basename(source))[0]
