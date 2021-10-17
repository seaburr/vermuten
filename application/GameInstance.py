import logging
import string
import random


class GameInstanceException(Exception):
    pass


class GameInstanceManager(object):

    GAME_KEY_LENGTH = 5

    def __init__(self, max_games):
        self.max_games = max_games
        self.game_instances = dict()

    def get_new_game_key(self):
        if len(self.game_instances) >= self.max_games:
            logging.error(f"There are already {len(self.game_instances)} active and only {self.max_games} are allowed.")
            raise GameInstanceException
        new_game_key = ""
        while new_game_key == "" and new_game_key not in self.game_instances:
            for i in range(self.GAME_KEY_LENGTH):
                i -= 1
                new_game_key += "".join(random.choice(string.hexdigits))
        return new_game_key.lower()

    def set_game_instance(self, game_key, game):
        self.game_instances[game_key] = game

    def get_game(self, game_key):
        if game_key in self.game_instances:
            return self.game_instances[game_key]
        else:
            logging.error(f"Could not find a game instance by key {game_key}")
            raise GameInstanceException

    def delete_game_instance(self, game_key):
        self.game_instances.pop(game_key)



