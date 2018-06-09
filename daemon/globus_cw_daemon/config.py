"""
Provides access to /etc/cwlogd.ini config values
"""
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

CONFIG_PATH = "/etc/cwlogd.ini"

class Config(object):

    def __init__(self, parser=None):
        """
        Either returns an already loaded configparser
        Or creates a configparser and loads ini config at /etc/cwlogd.ini
        """
        if parser is None:
            self._config = configparser.ConfigParser()
            self._config.read(CONFIG_PATH)
        else:
            self._config = parser


    def get_string(self, key):
        """
        Given a key returns the value of that key in config as a string.
        A KeyError will be raised if no constant with the given key exists.
        """
        try:
            return self._config.get("general", key)
        except configparser.NoOptionError:
            raise KeyError("key {0!r} not found".format(key))


    def get_bool(self, key):
        """
        Given a key returns the value of that key in config as a boolean.
        A KeyError will be raised if no constant with the given key exists.
        A ValueError will be raised if the constant cannot be a boolean.
        """
        try:
            return self._config.getboolean("general", key)
        except configparser.NoOptionError:
            raise KeyError("key {0!r} not found".format(key))


    def get_int(self, key):
        """
        Given a key returns the value of that key in config as an int.
        A KeyError will be raised if no constant with the given key exists.
        A ValueError will be raised if the constant cannot be an int.
        """
        try:
            return self._config.getint("general", key)
        except configparser.NoOptionError:
            raise KeyError("key {0!r} not found".format(key))
