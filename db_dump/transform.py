from tools import get_mongodb_db, drop_all_collections, build_df_from_collection, extend_df_with_collection

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
print("Participants are loaded: {}".format(df.shape[0]))

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
            'date_str': '$_id.date',
            'level_str': '$last_level',
            'when_created': '$when_created'
        }
    }
]

# create a dataframe from the aggregation result
daily = pd.DataFrame(db['bout_planning_notification_level'].aggregate(pipeline))
daily = daily[['user_id', 'date_str', 'level_str']]

# add a column of day_index per user_id, day_index is the number of days since the study start date from participant collection
participant_df = pd.DataFrame(participants_collection.find({}, {'_id': 0, 'user_id': 1, 'study_start_date': 1}))
daily = pd.merge(daily, participant_df, on='user_id', how='left')
daily['study_start_date'] = pd.to_datetime(daily['study_start_date'])
daily['date_dt'] = pd.to_datetime(daily['date_str'])
daily['day_index'] = (daily['date_dt'] - daily['study_start_date']).dt.days

# if day_index is less than 10, set level_str as "RE" and level_int as 0
daily.loc[daily['day_index'] < 10, 'level_str'] = "RE"
daily.loc[daily['day_index'] < 10, 'level_int'] = 0

# if day_index is greater than 252, set level_str as "FU" and level_int as 4
daily.loc[daily['day_index'] > 252, 'level_str'] = "FU"
daily.loc[daily['day_index'] > 252, 'level_int'] = 4

# convert level_str to level_int
level_categories = ["RE", "RA", "NR", "NO", "FU"]
daily['level_int'] = pd.Categorical(daily['level_str'], categories=level_categories, ordered=True).codes

# drop the columns that are not needed
daily = daily[['user_id', 'date_str', 'date_dt', 'day_index', 'level_str', 'level_int']]

print("Intervention components are loaded: {}".format(daily.shape[0]))
print(daily.sort_values(by=['user_id', 'date_str'], ascending=True))

# 2.2. find the `step_goal` from daily_step_goals_stepgoal, for each user_id and date, there are multiple goals, we only need the last goal by created column

pipeline = [
    {
        '$match': {'user_id': {'$in': participant_list}}
    },
    {
        '$sort': {'created': 1}
    },
    {
        '$group': {
            '_id': {'user_id': '$user_id', 'date': '$date'},
            'last_goal': {'$last': '$step_goal'},
            'created': {'$last': '$created'}
        }
    },
    {
        '$project': {
            '_id': 0,
            'user_id': '$_id.user_id',
            'date_str': '$_id.date',
            'step_goal': '$last_goal'
        }
    }
]

# create a dataframe from the aggregation result
temp_goals_df = pd.DataFrame(db['daily_step_goals_stepgoal'].aggregate(pipeline))

# merge the step_goal with daily dataframe
daily = pd.merge(daily, temp_goals_df, on=['user_id', 'date_str'], how='right')

print("Goals are loaded: {}".format(daily.shape[0]))
print(daily.sort_values(by=['user_id', 'date_str'], ascending=True))






# 3. insert the data into the database
daily_collection = tdb['daily']

# clean up the data before inserting into the database
daily['date_dt'] = pd.to_datetime(daily['date_str'])
daily = pd.merge(daily, participant_df, on='user_id', how='left')
daily['study_start_date'] = pd.to_datetime(daily['study_start_date'])
daily['day_index'] = (daily['date_dt'] - daily['study_start_date']).dt.days

# if day_index is less than 10, set level_str as "RE" and level_int as 0
daily.loc[daily['day_index'] < 10, 'level_str'] = "RE"
daily.loc[daily['day_index'] < 10, 'level_int'] = 0

# if day_index is greater than 252, set level_str as "FU" and level_int as 4
daily.loc[daily['day_index'] > 252, 'level_str'] = "FU"
daily.loc[daily['day_index'] > 252, 'level_int'] = 4

daily_collection.insert_many(daily.to_dict('records'))