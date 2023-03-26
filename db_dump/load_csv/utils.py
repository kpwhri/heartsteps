from config import MONGO_DB_URI_DESTINATION
from pymongo import MongoClient
import pandas as pd

def get_database(uri:str, database_name:str):
    client = MongoClient(uri)
    return client[database_name]

def get_participant_list():
    db = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')
    participants = db['participants']
    return list(participants.distinct(key='user_id'))