from tools import get_mongodb_db, drop_all_collections, build_df_from_collection, extend_df_with_collection

import streamlit as st
import pandas as pd
import numpy as np
import os
import pymongo

from pymongo import MongoClient

# This program is used to transform the data from the database dump (justwalk database, 'db') into a format that is more suitable for the data analysis (transformed database, 'tdb')

version = '0.1.1'

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



# 1. participants
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
st.write("Participants are loaded: {}".format(df.shape[0]))

participants_collection = tdb['participants']
participants_collection.insert_many(df.to_dict('records'))
participant_list = df['user_id'].tolist()

# 2. intervention_components

# 2.1. find the level from bout_planning_notification_level collection for each user_id and date, for each user_id and date, there are multiple levels, we only need the last level by when_created column

pipeline = [
    {
        '$match': {'user_id': {'$in': participant_list}}
    },
    {
        '$sort': {'when_created': 1}
    },
    {
        '$group': {
            '_id': {'user_id': '$user_id', 'date': '$date'},
            'last_level': {'$last': '$level'},
            'when_created': {'$last': '$when_created'}
        }
    },
    {
        '$project': {
            '_id': 0,
            'user_id': '$_id.user_id',
            'date': '$_id.date',
            'level': '$last_level',
            'when_created': '$when_created'
        }
    }
]


df = pd.DataFrame(db['bout_planning_notification_level'].aggregate(pipeline))
df = df[['user_id', 'date', 'level']]

# add a column of day_index per user_id, day_index is the number of days since the study start date
df['day_index'] = df.groupby('user_id')['date'].rank(method='first')

st.write("Intervention components are loaded: {}".format(df.shape[0]))
st.write(df.sort_values(by=['user_id', 'date'], ascending=True))

intervention_levels_collection = tdb['intervention_levels']
intervention_levels_collection.insert_many(df.to_dict('records'))


# 2.1.1 draw a heatmap of the levels, x axis is the date, y axis is the user_id (ordered), color is the level, add the legend, add the title, add a slider to select the date range

import seaborn as sns
import matplotlib.pyplot as plt
import datetime

# Convert date to datetime format
df['date'] = pd.to_datetime(df['date'])
level_categories = ["RE", "RA", "NR", "NO", "FU"]
df['level'] = pd.Categorical(df['level'], categories=level_categories, ordered=True).codes

# Pivot dataframe to create heatmap data
heatmap_data = df.pivot_table(index='user_id', columns='date', values='level', aggfunc=np.sum)

# Create a Streamlit slider to select date range
start_date = st.date_input('Start date', datetime.date(2022, 1, 1))
end_date = st.date_input('End date', datetime.date(2023, 12, 31))

# Convert date objects to datetime objects
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter heatmap data based on the selected date range
mask = (heatmap_data.columns >= start_date) & (heatmap_data.columns <= end_date)
filtered_heatmap_data = heatmap_data.loc[:, mask]

# Create heatmap
plt.figure(figsize=(15, 10))
sns.heatmap(filtered_heatmap_data, cmap='viridis', cbar_kws={'ticks': [0, 1, 2, 3, 4]})

# Add title, legend and labels
plt.title('User Levels Heatmap')
plt.xlabel('Date')
plt.ylabel('User ID')

# Add legend
plt.legend(title='Level', labels=level_categories)

# Display heatmap in Streamlit
st.pyplot(plt.gcf())

