import logging
import string
import random


class GameInstanceException(Exception):
    pass


class GameInstanceManager(object):

    GAME_KEY_LENGTH = 5

    def __init__(self, max_games):
        self.max_games = max_games
        self.used_keys = list()
        self.game_instances = dict()
        self.game_admins = dict()

    def _generate_key(self):
        new_game_key = ""
        while new_game_key == "" and new_game_key not in self.used_keys:
            for i in range(self.GAME_KEY_LENGTH):
                i -= 1
                new_game_key += "".join(random.choice(string.hexdigits))
        self.used_keys.append(new_game_key.lower())
        return new_game_key.lower()

    def get_game_key_set(self):
        return self._generate_key(), self._generate_key()

    def set_game_instance(self, game_key, admin_key, game):
        if len(self.game_instances) < self.max_games:
            self.game_instances[game_key] = game
            self.game_admins[admin_key] = game_key
        else:
            logging.error(f"There are too many active games right now.")
            raise GameInstanceException

    def get_game_by_game_key(self, game_key):
        if game_key in self.game_instances:
            return self.game_instances[game_key]
        else:
            logging.error(f"Could not find a game instance by key {game_key}")
            raise GameInstanceException

    def get_game_by_admin_key(self, admin_key):
        if admin_key in self.game_admins:
            game_key = self.game_admins[admin_key]
            return self.game_instances[game_key]
        else:
            logging.error(f"Could not find a game instance by key {admin_key}")
            raise GameInstanceException

    def get_game_key_by_admin_key(self, admin_key):
        if admin_key in self.game_admins:
            return self.game_admins[admin_key]
        else:
            logging.error(f"Could not find a game key by admin key {admin_key}")
            raise GameInstanceException

    def delete_game_instance(self, game_key, admin_key):
        logging.warning(f"Deleting game {game_key}")
        self.game_instances.pop(game_key)
        self.game_admins.pop(admin_key)
        self.used_keys.remove(game_key)
        self.used_keys.remove(admin_key)

    def delete_oldest_game(self):
        game_key = list(self.game_instances.keys())[0]
        admin_key = list(self.game_admins.keys())[0]
        self.delete_game_instance(game_key, admin_key)


