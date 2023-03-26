from config import MONGO_DB_URI_SOURCE, SETTINGS_CSV_PATH
from utils import get_database

import logging
import pandas as pd
import numpy as np
import os
import pymongo
import ray

from pymongo import MongoClient

def load_csv_to_local_mongodb():
    # Path: db_dump/dump_loader_gui.py
    path = SETTINGS_CSV_PATH

    # create a client instance of the MongoClient class
    db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')

    meta = db['meta']
    # put the dump path and the date into the meta collection
    logging.info(f'Inserting dump path and date into meta collection')
    meta.insert_one({'action': 'dump', 'path': path, 'date': pd.Timestamp.today(), 'when': pd.Timestamp.now()})

    # list all csv files in the folder
    logging.info(f'Listing all csv files in the folder')
    files = os.listdir(path)
    files_csv = [file for file in files if file.endswith('.csv')]
    files_csv.sort()
    file_count = len(files_csv)
    logging.info(f'Found {file_count} csv files')

    

    logging.info(f'Loading csv files to local mongodb')
    ray.get([load_each_csv_to_local_mongodb.remote(i, file, file_count) for i, file in enumerate(files_csv)])
    logging.info(f'Completed loading csv files to local mongodb')

@ray.remote
def load_each_csv_to_local_mongodb(i, file, file_count):
    start_time = pd.Timestamp.now()

    path = SETTINGS_CSV_PATH

    # create a client instance of the MongoClient class
    db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')

    # show the message on the screen
    logging.info(f'Reading in file {i + 1} of {file_count}: {file} (file size: {int(os.path.getsize(path + "/" + file) / 1000000)} MB))')

    # read the csv file
    df = pd.read_csv(path + '/' + file)
    
    # run only if the dataframe is not empty
    if not df.empty:    
        # show the file name on the screen
        logging.info(f'Processing file {i + 1} of {file_count}: {file} (row count: {df.shape[0]}, file size: {int(os.path.getsize(path + "/" + file) / 1000000)} MB))')

        # get the collection name
        collection_name = file.split('.')[0]

        # create a collection instance
        collection = db[collection_name]

        # check the document count and if the document count is the same as the row count, skip the file
        if collection.count_documents({}) != df.shape[0]:    
            # clear the collection
            logging.info(f'Clearing collection {collection_name}')
            collection.delete_many({})

            # insert data into the collection
            logging.info(f'Inserting data into collection {collection_name}')
            collection.insert_many(df.to_dict('records'), ordered=False)
    
    end_time = pd.Timestamp.now()
    logging.info(f'Completed file {i + 1} of {file_count}: {file}, took {end_time - start_time} seconds')