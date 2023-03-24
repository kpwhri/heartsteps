from tools import get_mongodb_db

import streamlit as st
import pandas as pd
import numpy as np
import os
import pymongo

from pymongo import MongoClient

# This program is used to transform the data from the database dump (justwalk database, 'db') into a format that is more suitable for the data analysis (transformed database, 'tdb')

version = '0.1.0'

# Path: db_dump/transform.py
pymongo_uri = 'mongodb://root:example@localhost:27017'
refresh_force = True

# create a client instance of the MongoClient class
client = MongoClient(pymongo_uri)

# create a database instance
db = client['justwalk']
tdb = get_mongodb_db()

# insert a meta data
meta = tdb['meta']

# put the dump path and the date into the meta collection
meta.insert_one({'action': 'transform', 'date': pd.Timestamp.today(),
                'when': pd.Timestamp.now(), 'version': version})

# 1. filter only the JustWalk study, and only the data from its participants


def filter_collection(db, tdb, collection_name, filter_dict, projection_dict, refresh_force=False) -> list:
    """
    Filter the collection and insert the filtered data into the transformed database.
    :param db: the database instance
    :param tdb: the transformed database instance
    :param collection_name: the collection name
    :param filter_dict: the filter dictionary
    :param projection_dict: the projection dictionary
    :return: the filtered data as a list of dictionaries
    """
    collection_source = db[collection_name]
    df = pd.DataFrame(
        list(collection_source.find(filter_dict, projection_dict)))
    collection_target = tdb[collection_name]

    # insert the data into the collection only if the collection's document count is not the same as the dataframe's row count
    if refresh_force or collection_target.count_documents({}) != df.shape[0]:
        collection_target.delete_many({})
        df_dict = df.to_dict('records')
        collection_target.insert_many(df_dict, ordered=False)
        return df_dict
    else:
        return list(collection_target.find({}, projection_dict))


study = filter_collection(db, tdb, 'participants_study', {
    'name': 'JustWalk'}, {'_id': 0, 'id': 1, 'name': 1, 'baseline_period': 1}, refresh_force)

study_id = study[0]['id']
st.write("Study ID: ", study_id)

# 2. filter only the cohort in the JustWalk study
cohort = filter_collection(db, tdb, 'participants_cohort', {
                           'study_id': study_id}, {'_id': 0, 'id': 1, 'name': 1, 'study_length': 1}, refresh_force)

cohort_id = cohort[0]['id']
st.write("Cohort ID: ", cohort_id)


# 3. filter only the participants in the JustWalk study and cohort
participants = filter_collection(db, tdb, 'participants_participant', {'cohort_id': cohort_id},
    {'heartsteps_id': 1, 'user_id': 1, 'birth_year': 1, 'study_start_date': 1}, refresh_force)

st.write("Number of participants: ", len(participants))

