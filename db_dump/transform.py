from tools import get_mongodb_db, drop_all_collections, build_df_from_collection, extend_df_with_collection

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

#########
drop_all_collections(tdb)   # Only for development
#########


# insert a meta data
meta = tdb['meta']

# put the dump path and the date into the meta collection
meta.insert_one({'action': 'transform', 'date': pd.Timestamp.today().strftime('%Y-%m-%d'),
                'when': pd.Timestamp.now(), 'version': version})


df = build_df_from_collection(db, 'participants_study', {'name': 'JustWalk'}, {
                              '_id': 0, 'id': 1, 'name': 1, 'baseline_period': 1},
                              rename_columns={'id': 'study_id', 'name': 'study_name'})
study_id = int(df['study_id'][0])

df = extend_df_with_collection(df, db, 'participants_cohort', {'study_id': study_id}, {
                               '_id': 0, 'id': 1, 'study_id': 1, 'name': 1, 'study_length': 1}, on='study_id', rename_columns={'id': 'cohort_id', 'name': 'cohort_name'})
cohort_id = int(df['cohort_id'][0])

df = extend_df_with_collection(df, db, 'participants_participant', {'cohort_id': cohort_id}, {
                                 '_id': 0, 'heartsteps_id': 1, 'cohort_id': 1, 'user_id': 1, 'birth_year': 1, 'study_start_date': 1}, on='cohort_id')

df = df[['heartsteps_id', 'user_id', 'birth_year', 'study_start_date']]
st.write(df)

participants_collection = tdb['participants']
participants_collection.insert_many(df.to_dict('records'))

# # 3. filter only the participants in the JustWalk study and cohort
# participants = filter_collection(db, tdb, 'participants_participant', {'cohort_id': cohort_id},
#                                  {'heartsteps_id': 1, 'user_id': 1, 'birth_year': 1, 'study_start_date': 1}, refresh_force)

# st.write("Number of participants: ", len(participants))
