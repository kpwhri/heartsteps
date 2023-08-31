# config.py
import configparser
import os
import logging

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

MONGO_DB_URI_SOURCE = config.get("MongoDB.Source", "URI")
MONGO_DB_URI_DESTINATION = config.get("MongoDB.Destination", "URI")
MONGO_DB_DESTINATION_DBNAME = config.get("MongoDB.Destination", "DBNAME")

SETTINGS_REFRESH_COLLECTIONS = config.get("Settings", "REFRESH_COLLECTIONS").split(',')

LOGGING_LEVEL = config.get("Logging", "LEVEL")
LOGGING_FORMAT = config.get("Logging", "FORMAT")
LOGGING_DATE_FORMAT = config.get("Logging", "DATE_FORMAT")
logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT, datefmt=LOGGING_DATE_FORMAT)
