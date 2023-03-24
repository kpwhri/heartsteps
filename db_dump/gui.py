import streamlit as st
import pandas as pd
import numpy as np
import os
import pymongo

from pymongo import MongoClient

# Path: db_dump/dump_loader_gui.py
path = '/Users/ffee21/justwalk_backup'
pymongo_uri = 'mongodb://root:example@localhost:27017'

# create a client instance of the MongoClient class
client = MongoClient(pymongo_uri)

# create a database instance
db = client['justwalk']

meta = db['meta']
# put the dump path and the date into the meta collection
meta.insert_one({'action': 'dump', 'path': path, 'date': pd.Timestamp.today(), 'when': pd.Timestamp.now()})

# list all csv files in the folder
files = os.listdir(path)
files_csv = [file for file in files if file.endswith('.csv')]
files_csv.sort()

# set the page width to 100%
st.set_page_config(layout="wide")

# show the progress bar with width 100%
my_bar = st.progress(0)

# create a textbox to show the completed files
my_message = st.empty()

file_count = len(files_csv)
for i, file in enumerate(files_csv):
    # show the message on the screen
    my_message.text(f'Reading in file {i + 1} of {file_count}: {file} (file size: {int(os.path.getsize(path + "/" + file) / 1000000)} MB))')

    # read the csv file
    df = pd.read_csv(path + '/' + file)
    
    # run only if the dataframe is not empty
    if not df.empty:    
        # show the file name on the screen
        my_message.text(f'Processing file {i + 1} of {file_count}: {file} (row count: {df.shape[0]}, file size: {int(os.path.getsize(path + "/" + file) / 1000000)} MB))')

        # get the collection name
        collection_name = file.split('.')[0]

        # create a collection instance
        collection = db[collection_name]

        # check the document count and if the document count is the same as the row count, skip the file
        if collection.count_documents({}) != df.shape[0]:    
            # clear the collection
            collection.delete_many({})

            # insert data into the collection
            collection.insert_many(df.to_dict('records'), ordered=False)

    # update the progress bar
    my_bar.progress((i + 1) / file_count)

    # write the completed filename on the screen
    my_message.text(f'Completed file {i + 1} of {file_count}: {file}')
