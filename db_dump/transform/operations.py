from geopy.geocoders import Nominatim
from geopy import distance
from config import SETTINGS_REFRESH_COLLECTIONS, MONGO_DB_URI_SOURCE, MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME
from utils import get_database, build_df_from_collection, extend_df_with_collection, get_participant_list, df_info, get_weather_observations_df_for_station
from constants import *
from tqdm import tqdm
import os
import pytz
import pandas as pd
import numpy as np
import ray
import logging
import pymongo
import datetime
from dateutil.parser import parse as dateparse
import time
import json
from pymongo import UpdateOne, InsertOne

import matplotlib.pyplot as plt
import seaborn as sns

import geopy

def transform_participants():
    if COLLECTION_PARTICIPANTS in SETTINGS_REFRESH_COLLECTIONS:
        # create a client instance of the MongoClient class
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

        # delete_many participants collection
        tdb.participants.delete_many({})

        # get the study id
        df = build_df_from_collection(db, 'participants_study', {'name': 'JustWalk'}, {
                                    '_id': 0, 'id': 1, 'name': 1, 'baseline_period': 1},
                                    rename_columns={'id': 'study_id', 'name': 'study_name'})
        study_id = int(df['study_id'][0])

        df = extend_df_with_collection(df, db, 'participants_cohort', {'study_id': study_id}, {
                                    '_id': 0, 'id': 1, 'study_id': 1, 'name': 1, 'study_length': 1}, on='study_id', rename_columns={'id': 'cohort_id', 'name': 'cohort_name'})
        cohort_id = int(df['cohort_id'][0])

        # get the participant list using the cohort_id
        df = extend_df_with_collection(df, db, 'participants_participant', {'cohort_id': cohort_id}, {
            '_id': 0, 'heartsteps_id': 1, 'cohort_id': 1, 'user_id': 1, 'birth_year': 1, 'study_start_date': 1}, on='cohort_id')

        # picking the columns that are needed
        df = df[['heartsteps_id', 'user_id', 'birth_year', 'study_start_date']].copy()
        
        # converting floats to integer
        df['birth_year'] = df['birth_year'].astype(int)
        df['user_id'] = df['user_id'].astype(int)

        logging.info("Participants are loaded: {}".format(df.shape[0]))

        participants_collection = tdb['participants']
        participants_collection.insert_many(df.to_dict('records'))
        participant_list = df['user_id'].tolist()

def transform_daily():
    if COLLECTION_DAILY in SETTINGS_REFRESH_COLLECTIONS:
        # create a client instance of the MongoClient class
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

        # delete_many participants collection
        tdb.daily.delete_many({})

        # get the study id list
        participant_list = get_participant_list()

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
        daily = pd.DataFrame(
            db['bout_planning_notification_level'].aggregate(pipeline))
        
        # convert the level_str to level_int
        daily['level_int'] = daily['level_str'].map({'RE': 0, 'RA': 1, 'NR': 2, 'NO': 3, 'FU': 4})

        daily = daily[['user_id', 'date_str', 'level_str', 'level_int']].copy()

        # # add a column of day_index per user_id, day_index is the number of days since the study start date from participant collection
        # participant_df = pd.DataFrame(tdb[COLLECTION_PARTICIPANTS].find(
        #     {}, {'_id': 0, 'user_id': 1, 'study_start_date': 1}))
        # daily = pd.merge(daily, participant_df, on='user_id', how='left')
        # daily['study_start_date'] = pd.to_datetime(daily['study_start_date'])
        # daily['date_dt'] = pd.to_datetime(daily['date_str'])
        # daily['day_index'] = (daily['date_dt'] - daily['study_start_date']).dt.days

        # # generate an empty dataframe with user_id, study_start_date, day_index, date_dt
        # empty_df = pd.DataFrame(columns=['user_id', 'study_start_date', 'day_index', 'date_dt'])

        # # for each participant, generate the rows with day_index from 0 to 270
        # for user_id in tqdm(participant_list):
        #     temp_df = pd.DataFrame({'user_id': [user_id] * 271})
        #     temp_df['study_start_date'] = participant_df.loc[participant_df['user_id'] == user_id, 'study_start_date'].iloc[0]
        #     temp_df['day_index'] = range(271)
        #     temp_df['study_start_date_dt'] = pd.to_datetime(temp_df['study_start_date'])
        #     temp_df['date_dt'] = temp_df['study_start_date_dt'] + pd.to_timedelta(temp_df['day_index'], unit='d')
        #     temp_df['date_str'] = temp_df['date_dt'].dt.strftime('%Y-%m-%d')
        #     empty_df = pd.concat([empty_df, temp_df], ignore_index=True)

        # # join daily and empty_df dataframes together. if there is no level for a day, set level_str as "RE" and level_int as 0. If a row exists in daily but not in empty_df, drop the row
        # daily = pd.merge(empty_df, daily[['user_id', 'day_index', 'date_str', 'level_str']], on=['user_id', 'day_index', 'date_str'], how='left')

        # # fill the NaNs with "RE"
        # daily['level_str'] = daily['level_str'].fillna("RE")
        

        # drop the columns that are not needed
        daily = daily[['user_id', 'date_str', 'level_str', 'level_int']].copy()

        # daily = daily[['user_id', 'date_str', 'date_dt', 'study_start_date',
        #             'day_index', 'level_str', 'level_int']].copy()

        logging.info("Levels and Step Goals are loaded: {}".format(daily.shape[0]))
        
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
        temp_goals_df = pd.DataFrame(
            db['daily_step_goals_stepgoal'].aggregate(pipeline))

        # merge the step_goal with daily dataframe
        daily = pd.merge(daily, temp_goals_df, on=['user_id', 'date_str'], how='outer')

        # # fill the NaNs with 2000
        # daily['step_goal'] = daily['step_goal'].fillna(2000)

        # logging.info("Goals are loaded: {}".format(daily.shape[0]))

        # 2.99. insert the data into the database
        daily_collection = tdb['daily']

        # # clean up the data before inserting into the database
        # daily['date_dt'] = pd.to_datetime(daily['date_str'])
        # daily['study_start_date'] = pd.to_datetime(daily['study_start_date'])
        
        # insert the data into the database
        daily_collection.insert_many(daily.to_dict('records'))

        # create index for user_id and date_str
        if 'user_id_date_str_unique_index' not in daily_collection.index_information():
            logging.info("Create index for user_id and date_str")
            daily_collection.create_index([('user_id', pymongo.ASCENDING), ('date_str', pymongo.ASCENDING)], unique=True, name='user_id_date_str_unique_index', background=True)
    else:
        logging.info("Daily data is already loaded, skip the loading process.")

def add_baseline_and_intervention_dates():
    # this function adds 1) baseline_start_date, 2) intervention_start_date, 3) intervention_finish_date to the participants collection
    if COLLECTION_PARTICIPANTS in SETTINGS_REFRESH_COLLECTIONS:
        logging.info("Starting add_baseline_and_intervention_dates()")
        # create a client instance of the MongoClient class
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

        # get the study id list
        participant_list = get_participant_list()

        for study_id in participant_list:
            # get all the dates from the daily collection
            daily_collection = tdb['daily']
            daily_df = pd.DataFrame(daily_collection.find({'user_id': study_id}, {'_id': 0, 'user_id': 1, 'date_str': 1, 'level_str': 1, 'level_int': 1, 'step_goal': 1}, sort=[('date_str', pymongo.ASCENDING)]))

            participants_collection = tdb['participants']
            participant_dict = participants_collection.find_one(
                {'user_id': study_id}
            )

            # find the first date with step_goal given
            baseline_start_date = daily_df.loc[daily_df['step_goal'].notnull(), 'date_str'].iloc[0]
            
            # find the first date with level_int >= 1
            # if any of the 'level_int' is >= 1, then the intervention_start_date is the first date with level_int >= 1. otherwise, the intervention_start_date should be set as None
            if daily_df['level_int'].max() >= 1:
                intervention_start_date = daily_df.loc[daily_df['level_int'] >= 1, 'date_str'].iloc[0]
                # set the intervention_finish_date as the last date with the intervention_start_date + 260 days
                intervention_finish_date = (dateparse(intervention_start_date) + datetime.timedelta(days=260)).strftime('%Y-%m-%d')
            
                # find the difference between the intervention_start_date and baseline_start_date
                baseline_start_date_dt = dateparse(baseline_start_date)
                intervention_start_date_dt = dateparse(intervention_start_date)
                baseline_intervention_diff = (intervention_start_date_dt - baseline_start_date_dt).days
            
                # find the difference between the baseline_start_date and study_start_date
                study_start_date = participant_dict['study_start_date']
                study_start_date_dt = dateparse(study_start_date)
                baseline_study_diff = (baseline_start_date_dt - study_start_date_dt).days
            else:
                intervention_start_date = None
                intervention_finish_date = None

            # update the participants collection with the baseline_start_date, intervention_start_date, intervention_finish_date
            participants_collection.update_one({'user_id': study_id}, {
                '$set': {
                    'baseline_start_date': baseline_start_date, 
                    'intervention_start_date': intervention_start_date, 
                    'intervention_finish_date': intervention_finish_date,
                    'baseline_intervention_diff': baseline_intervention_diff,
                    'baseline_study_diff': baseline_study_diff
                }})

            # add day_index column to the daily_df
            daily_df['day_index'] = (daily_df['date_str'].apply(dateparse) - intervention_start_date_dt).dt.days

            # update the daily collection with the day_index
            daily_collection.bulk_write([
                UpdateOne(
                    {'user_id': study_id, 'date_str': row['date_str']},
                    {'$set': {'day_index': row['day_index']}}
                ) for i, row in daily_df.iterrows()
            ])
    else:
        logging.info("Baseline and intervention dates are already added, skip the adding process.")

def drop_dates_after_intervention_finish_date():
    if COLLECTION_DAILY in SETTINGS_REFRESH_COLLECTIONS:
        # create a client instance of the MongoClient class
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

        daily_collection = tdb['daily']

        daily_collection.delete_many({"day_index": {"$gt": 259}})
        logging.info("Finished dropping the dates after the intervention finish date.")
    else:
        logging.info("Dates after the intervention finish date are already dropped, skip the dropping process.")

def transform_minute_step():
    if COLLECTION_MINUTE_STEP in SETTINGS_REFRESH_COLLECTIONS:
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

        # delete_many participants collection
        logging.debug(msg="Delete all documents in the collection: {}".format(COLLECTION_MINUTE_STEP))
        tdb.minute_step.delete_many({})

        # get the study id list
        logging.debug(msg="Get the study id list")
        participant_list = get_participant_list()

        fitbit_api_account_collection = db['fitbit_api_fitbitaccountuser']

        def get_timezone_span(user_id):
            db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
            tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

            # find the timezone info for each user_id
            timezone_df = pd.DataFrame(db.days_day.find({'user_id': user_id}, {'_id': 0, 'date': 1, 'timezone': 1}, sort=[('date', pymongo.ASCENDING)]))

            # merge the timezone span
            start_date = None
            end_date = None
            current_timezone = None
            timezone_span = []
            for i, row in timezone_df.iterrows():
                if start_date is None:
                    start_date = row['date']
                    current_timezone = row['timezone']
                elif current_timezone != row['timezone']:
                    end_date = row['date']
                    timezone_span.append({'start_date': start_date, 'end_date': end_date, 'timezone': current_timezone})
                    start_date = row['date']
                    current_timezone = row['timezone']
            end_date = timezone_df['date'].iloc[-1]
            timezone_span.append({'start_date': start_date, 'end_date': end_date, 'timezone': current_timezone})

            return timezone_span
        
        @ray.remote
        def process_minute_step_1(user_id):
            db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
            tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

            timezone_span = get_timezone_span(user_id)

            # find the fitbit account for each user_id
            fitbit_account_id = db.fitbit_api_fitbitaccountuser.find_one({'user_id': user_id}, {'_id': 0, 'account_id': 1})['account_id']
            
            # find the minute-level steps from fitbit_activities_fitbitminutestepcount collection for each user_id and minute
            for timezone in timezone_span:
                minute_step_df = pd.DataFrame(db.fitbit_activities_fitbitminutestepcount.find({'account_id': fitbit_account_id, 'time': {'$gte': timezone['start_date'], '$lt': timezone['end_date']}}, {'_id': 0, 'time': 1, 'steps': 1}))
                minute_agg_step_df = pd.DataFrame(columns=['user_id', 'date_str', 'steps'])

                if minute_step_df.shape[0] > 0:
                    # merge the minute-level steps with fitbit_api_account_df
                    minute_step_df['time'] = pd.to_datetime(
                        minute_step_df['time']).dt.tz_convert(timezone['timezone'])

                    # reorganize the minute-level steps to list of integers of each day. insert 0s for missing minutes
                    minute_step_df['date_str'] = minute_step_df['time'].dt.strftime('%Y-%m-%d')
                    minute_step_df['time_str'] = minute_step_df['time'].dt.strftime('%H:%M')
                    minute_step_df['user_id'] = user_id

                    tdb.temp_minute_step.insert_many(minute_step_df.to_dict('records'))

        @ray.remote
        def process_minute_step_2(user_id):
            db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
            tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

            participant_collection = tdb['participants']

            minute_step_df = pd.DataFrame(tdb.temp_minute_step.find({'user_id': user_id}, {'_id': 0, 'user_id': 1, 'date_str': 1, 'time_str': 1, 'steps': 1}))
            
            if minute_step_df.shape[0] > 0:
                minute_agg_step_df = pd.DataFrame(columns=['user_id', 'date_str', 'steps'])
                date_str_list = minute_step_df['date_str'].unique().tolist()
                first_date_str = participant_collection.find_one({'user_id': user_id}, {'_id': 0, 'baseline_start_date': 1})['baseline_start_date']
                last_date_str = participant_collection.find_one({'user_id': user_id}, {'_id': 0, 'intervention_finish_date': 1})['intervention_finish_date']
                
                # prepare the list of all the date_str
                if first_date_str is None or last_date_str is None:
                    return
                date_str_list = [dateparse(first_date_str) + datetime.timedelta(days=x) for x in range((dateparse(last_date_str) - dateparse(first_date_str)).days + 1)]
                date_str_list = [x.strftime('%Y-%m-%d') for x in date_str_list]

                for date_str in date_str_list:
                    user_date_df = minute_step_df.loc[minute_step_df['date_str'] == date_str, ['time_str', 'steps']]

                    if user_date_df.shape[0] > 0:
                        minutes = [0] * 24 * 60

                        for i, row in user_date_df.iterrows():
                            minutes[dateparse(row['time_str']).hour * 60 + dateparse(row['time_str']).minute] = row['steps']
                        
                        minute_agg_step_df = pd.concat([minute_agg_step_df, pd.DataFrame({'user_id': user_id, 'date_str': date_str, 'steps': [minutes]})], ignore_index=True)
                    else:
                        minute_agg_step_df = pd.concat([minute_agg_step_df, pd.DataFrame({'user_id': user_id, 'date_str': date_str, 'steps': [[0] * 24 * 60]})], ignore_index=True)
                
                # insert the steps list into the minute_step collection
                minute_step_collection_t = tdb['minute_step']
                minute_step_collection_t.insert_many(minute_agg_step_df.to_dict('records'))


        tdb.temp_minute_step.delete_many({})

        # run the ray tasks
        logging.info(msg="Pre-loading the data to process minute steps for {} users".format(len(participant_list)))
        process_minute_step_list_future = [
            process_minute_step_1.remote(user_id) for user_id in participant_list
        ]

        logging.info(msg="Waiting for the ray tasks to finish")
        ray.get(process_minute_step_list_future, timeout=3600)
        logging.info(msg="Finished waiting for the ray tasks to finish.")

        # add the index for user_id
        if 'user_id_index' not in tdb.temp_minute_step.index_information():
            logging.info(msg="Create index for user_id")
            tdb.temp_minute_step.create_index([('user_id', pymongo.ASCENDING)], name='user_id_index', background=True)

        # run the ray tasks
        logging.info(msg="Pre-loading the data to process minute steps for {} users".format(len(participant_list)))
        process_minute_step_list_future = [
            process_minute_step_2.remote(user_id) for user_id in participant_list
        ]

        logging.info(msg="Waiting for the ray tasks to finish")
        ray.get(process_minute_step_list_future, timeout=3600)
        logging.info(msg="Finished waiting for the ray tasks to finish.")



        # delete the temp_minute_step collection
        tdb.drop_collection('temp_minute_step')
        # sum the minute-level steps into daily-level steps
        pipeline = [
            {
                '$match': {'user_id': {'$in': participant_list}}
            },
            {
                '$unwind': '$steps'
            },
            {
                '$group': {
                    '_id': {'user_id': '$user_id', 'date_str': '$date_str'},
                    'steps': {'$sum': '$steps'}
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'user_id': '$_id.user_id',
                    'date_str': '$_id.date_str',
                    'steps': '$steps'
                }
            }
        ]

        # create a dataframe from the aggregation result
        minute_agg_step_df = pd.DataFrame(
            tdb['minute_step'].aggregate(pipeline))
        
        # update the daily collection with the daily-level steps
        daily_collection = tdb['daily']
        daily_collection.bulk_write([
            UpdateOne(
                {'user_id': row['user_id'], 'date_str': row['date_str']},
                {'$set': {'steps': row['steps']}}
            ) for i, row in minute_agg_step_df.iterrows()
        ])

def transform_minute_heart_rate():
    if COLLECTION_MINUTE_HEART_RATE in SETTINGS_REFRESH_COLLECTIONS:
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

        # delete_many participants collection
        logging.debug(msg="Delete all documents in the collection: {}".format(COLLECTION_MINUTE_HEART_RATE))
        tdb.minute_heart_rate.delete_many({})

        # get the study id list
        logging.debug(msg="Get the study id list")
        participant_list = get_participant_list()

        fitbit_api_account_collection = db['fitbit_api_fitbitaccountuser']

        def get_timezone_span(user_id):
            db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
            tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

            # find the timezone info for each user_id
            timezone_df = pd.DataFrame(db.days_day.find({'user_id': user_id}, {'_id': 0, 'date': 1, 'timezone': 1}, sort=[('date', pymongo.ASCENDING)]))

            # merge the timezone span
            start_date = None
            end_date = None
            current_timezone = None
            timezone_span = []
            for i, row in timezone_df.iterrows():
                if start_date is None:
                    start_date = row['date']
                    current_timezone = row['timezone']
                elif current_timezone != row['timezone']:
                    end_date = row['date']
                    timezone_span.append({'start_date': start_date, 'end_date': end_date, 'timezone': current_timezone})
                    start_date = row['date']
                    current_timezone = row['timezone']
            end_date = timezone_df['date'].iloc[-1]
            timezone_span.append({'start_date': start_date, 'end_date': end_date, 'timezone': current_timezone})

            return timezone_span
        
        @ray.remote
        def process_minute_heart_rate_1(user_id):
            db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
            tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

            timezone_span = get_timezone_span(user_id)

            # find the fitbit account for each user_id
            fitbit_account_id = db.fitbit_api_fitbitaccountuser.find_one({'user_id': user_id}, {'_id': 0, 'account_id': 1})['account_id']
            
            # find the minute-level heart rate from fitbit_activities_fitbitminuteheartrate collection for each user_id and minute
            for timezone in timezone_span:
                minute_heart_rate_df = pd.DataFrame(db.fitbit_activities_fitbitminuteheartrate.find({'account_id': fitbit_account_id, 'time': {'$gte': timezone['start_date'], '$lt': timezone['end_date']}}, {'_id': 0, 'time': 1, 'heart_rate': 1}))
                minute_agg_heart_rate_df = pd.DataFrame(columns=['user_id', 'date_str', 'heart_rate'])

                if minute_heart_rate_df.shape[0] > 0:
                    # merge the minute-level heart rate with fitbit_api_account_df
                    minute_heart_rate_df['time'] = pd.to_datetime(
                        minute_heart_rate_df['time']).dt.tz_convert(timezone['timezone'])

                    # reorganize the minute-level heart_rate to list of integers of each day. insert 0s for missing minutes
                    minute_heart_rate_df['date_str'] = minute_heart_rate_df['time'].dt.strftime('%Y-%m-%d')
                    minute_heart_rate_df['time_str'] = minute_heart_rate_df['time'].dt.strftime('%H:%M')
                    minute_heart_rate_df['user_id'] = user_id

                    tdb.temp_minute_heart_rate.insert_many(minute_heart_rate_df.to_dict('records'))

        @ray.remote
        def process_minute_heart_rate_2(user_id):
            db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
            tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

            participant_collection = tdb['participants']

            minute_heart_rate_df = pd.DataFrame(tdb.temp_minute_heart_rate.find({'user_id': user_id}, {'_id': 0, 'user_id': 1, 'date_str': 1, 'time_str': 1, 'heart_rate': 1}))
            
            if minute_heart_rate_df.shape[0] > 0:
                minute_agg_heart_rate_df = pd.DataFrame(columns=['user_id', 'date_str', 'heart_rate'])
                date_str_list = minute_heart_rate_df['date_str'].unique().tolist()
                first_date_str = participant_collection.find_one({'user_id': user_id}, {'_id': 0, 'baseline_start_date': 1})['baseline_start_date']
                last_date_str = participant_collection.find_one({'user_id': user_id}, {'_id': 0, 'intervention_finish_date': 1})['intervention_finish_date']
                
                # prepare the list of all the date_str
                if first_date_str is None or last_date_str is None:
                    return
                date_str_list = [dateparse(first_date_str) + datetime.timedelta(days=x) for x in range((dateparse(last_date_str) - dateparse(first_date_str)).days + 1)]
                date_str_list = [x.strftime('%Y-%m-%d') for x in date_str_list]

                for date_str in date_str_list:
                    user_date_df = minute_heart_rate_df.loc[minute_heart_rate_df['date_str'] == date_str, ['time_str', 'heart_rate']]

                    if user_date_df.shape[0] > 0:
                        minutes = [0] * 24 * 60

                        for i, row in user_date_df.iterrows():
                            minutes[dateparse(row['time_str']).hour * 60 + dateparse(row['time_str']).minute] = row['heart_rate']
                        
                        minute_agg_heart_rate_df = pd.concat([minute_agg_heart_rate_df, pd.DataFrame({'user_id': user_id, 'date_str': date_str, 'heart_rate': [minutes]})], ignore_index=True)
                    else:
                        minute_agg_heart_rate_df = pd.concat([minute_agg_heart_rate_df, pd.DataFrame({'user_id': user_id, 'date_str': date_str, 'heart_rate': [[0] * 24 * 60]})], ignore_index=True)
                
                # insert the heart_rate list into the minute_heart_rate collection
                minute_heart_rate_collection_t = tdb['minute_heart_rate']
                minute_heart_rate_collection_t.insert_many(minute_agg_heart_rate_df.to_dict('records'))


        tdb.temp_minute_heart_rate.delete_many({})

        # run the ray tasks
        logging.info(msg="Pre-loading the data to process minute heart rate for {} users".format(len(participant_list)))
        process_minute_heart_rate_list_future = [
            process_minute_heart_rate_1.remote(user_id) for user_id in participant_list
        ]

        logging.info(msg="Waiting for the ray tasks to finish")
        ray.get(process_minute_heart_rate_list_future, timeout=3600)
        logging.info(msg="Finished waiting for the ray tasks to finish.")

        # add the index for user_id
        if 'user_id_index' not in tdb.temp_minute_heart_rate.index_information():
            logging.info(msg="Create index for user_id")
            tdb.temp_minute_heart_rate.create_index([('user_id', pymongo.ASCENDING)], name='user_id_index', background=True)

        # run the ray tasks
        logging.info(msg="Pre-loading the data to process minute steps for {} users".format(len(participant_list)))
        process_minute_heart_rate_list_future = [
            process_minute_heart_rate_2.remote(user_id) for user_id in participant_list
        ]

        logging.info(msg="Waiting for the ray tasks to finish")
        ray.get(process_minute_heart_rate_list_future, timeout=3600)
        logging.info(msg="Finished waiting for the ray tasks to finish.")



        # delete the temp_minute_step collection
        tdb.drop_collection('temp_minute_heart_rate')
        # count the number of non-zero minutes
        pipeline = [
            {
                '$match': {'user_id': {'$in': participant_list}}
            },
            {
                '$unwind': '$heart_rate'
            },
            {
                '$group': {
                    '_id': {'user_id': '$user_id', 'date_str': '$date_str'},
                    'wearing_minutes': {'$sum': {'$cond': [{'$gt': ['$heart_rate', 0]}, 1, 0]}}
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'user_id': '$_id.user_id',
                    'date_str': '$_id.date_str',
                    'wearing_minutes': '$wearing_minutes'
                }
            }
        ]

        # create a dataframe from the aggregation result
        minute_agg_heart_rate_df = pd.DataFrame(
            tdb['minute_heart_rate'].aggregate(pipeline))
        
        # update the daily collection with the daily-level wearing_minutes
        daily_collection = tdb['daily']
        daily_collection.bulk_write([
            UpdateOne(
                {'user_id': row['user_id'], 'date_str': row['date_str']},
                {'$set': {'wearing_minutes': row['wearing_minutes']}}
            ) for i, row in minute_agg_heart_rate_df.iterrows()
        ])

def add_zip_codes():
    zipcode_csv_path = 'db_dump/data/zipcode/zipcode.csv'
    if COLLECTION_PARTICIPANTS in SETTINGS_REFRESH_COLLECTIONS and os.path.exists(zipcode_csv_path):
        print("Zipcode file is found. Trying to import the data.")

        # create a client instance of the MongoClient class
        db = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

        # load up the csv file
        zipcode_df = pd.read_csv(zipcode_csv_path, dtype={'zip': str})

        # check if the participants collection has the heartsteps_id index
        if 'heartsteps_id_unique_index' not in db.participants.index_information():
            logging.info("Create index for heartsteps_id")
            db.participants.create_index([('heartsteps_id', pymongo.ASCENDING)], unique=True, name='heartsteps_id_unique_index', background=True)
        
        # update the participants collection with the zip code
        participants_collection = db['participants']
        participants_collection.bulk_write([
            UpdateOne(
                {'heartsteps_id': row['heartsteps_id']},
                {'$set': {'zipcode': row['zipcode']}}
            ) for i, row in zipcode_df.iterrows()
        ])

def add_weather():
    if COLLECTION_DAILY in SETTINGS_REFRESH_COLLECTIONS:
        weather_path = 'db_dump/data/weather/weather.csv'
        if not os.path.exists(weather_path):
            # we should fetch the weather data from the NOAA
            print("Weather file is not found. Trying to fetch the data from NCEI.")
            
            def geocode_zipcode(zipcode: str):
                def __geocode_zipcode(zipcode: str):
                    def get_geolocator_client():
                        return Nominatim(user_agent="justwalk_ucsd_edu")

                    geolocator = get_geolocator_client()
                    location = geolocator.geocode(zipcode, country_codes="US")

                    return location[-1][0], location[-1][1]

                latitude, longitude = __geocode_zipcode(zipcode)
                print("Geocoding zipcode {} to {}, {}".format(zipcode, latitude, longitude))

                return latitude, longitude


            # list up all zipcodes
            db = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

            zipcode_latlon_csv_path = 'db_dump/data/zipcode/zipcode_latlon.csv'
            if os.path.exists(zipcode_latlon_csv_path):
                zipcode_df = pd.read_csv(zipcode_latlon_csv_path, dtype={'zipcode': str})
                zipcode_list = zipcode_df['zipcode'].tolist()
            else:
                participants_collection = db['participants']
                zipcode_list = participants_collection.distinct('zipcode')

                # pad the zipcode with 0s while casting integers to string
                zipcode_list = [str(x).zfill(5) for x in zipcode_list]

                
                
                zipcode_df = pd.DataFrame(columns=['zipcode', 'latitude', 'longitude'])
                for zipcode in zipcode_list:
                    latitude, longitude = geocode_zipcode(zipcode)
                    zipcode_df = pd.concat([zipcode_df, pd.DataFrame({'zipcode': [zipcode], 'latitude': [latitude], 'longitude': [longitude]})], ignore_index=True)
                
            ncei_station_filename = 'db_dump/data/zipcode/weather.ncei_stations.csv'
            ncei_station_df = pd.read_csv(ncei_station_filename, dtype={'station_id': str})

            def get_closest_stations(ncei_station_df, latitude, longitude, n=10):
                distance_df = pd.DataFrame(columns=['station_id', 'distance'])
                for i, row in ncei_station_df.iterrows():
                    distance = geopy.distance.distance((latitude, longitude), (row['latitude'], row['longitude'])).km
                    distance_df = pd.concat([distance_df, pd.DataFrame({'station_id': [row['station_id']], 'distance': [distance]})], ignore_index=True)

                distance_df = distance_df.sort_values(by=['distance'], ascending=True)
                return distance_df.iloc[:n, :].copy()
            
            def get_weather_station_df(zipcode):
                latitude, longitude = geocode_zipcode(zipcode)
                closest_stations_df = get_closest_stations(ncei_station_df, latitude, longitude, n=10)
                closest_stations_df = closest_stations_df.merge(ncei_station_df, on=['station_id'], how='left')
                closest_stations_df['zipcode'] = zipcode

                return closest_stations_df[['zipcode', 'station_id', 'latitude', 'longitude']].copy()
            
            def get_weather_observations_df(zipcode, start_date, end_date):
                latitude, longitude = geocode_zipcode(zipcode)
                closest_stations_df = get_closest_stations(ncei_station_df, latitude, longitude, n=10)
                closest_stations_df = closest_stations_df.merge(ncei_station_df, on=['station_id'], how='left')
                closest_stations_df['zipcode'] = zipcode

                # fetch the weather data from the NOAA
                df = pd.DataFrame()
                for i, row in closest_stations_df.iterrows():
                    print("Fetching the weather data for station_id: {}".format(row['station_id']))
                    df = pd.concat([df, get_weather_observations_df_for_station(row['station_id'], start_date, end_date)], ignore_index=True)
                
                return df



            # search the weather station for each zipcode
            weather_station_df_filepath = 'db_dump/data/zipcode/weather_station_df.csv'
            if os.path.exists(weather_station_df_filepath):
                weather_station_df = pd.read_csv(weather_station_df_filepath, dtype={'zipcode': str, 'station_id': str})
            else:
                weather_station_df = pd.DataFrame(columns=['zipcode', 'station_id', 'latitude', 'longitude'])
                for zipcode in zipcode_list:
                    print("Searching the weather station for zipcode: {}".format(zipcode))
                    station_df = get_weather_station_df(zipcode)
                    if station_df is not None:
                        weather_station_df = pd.concat([weather_station_df, station_df], ignore_index=True)
                weather_station_df.to_csv(weather_station_df_filepath, index=False)
            
            station_list = weather_station_df['station_id'].unique().tolist()

            weather_raw_df_filepath = 'db_dump/data/weather/weather_raw_df.csv'
            if os.path.exists(weather_raw_df_filepath):
                weather_raw_df = pd.read_csv(weather_raw_df_filepath, dtype={'station_id': str})
            else:
                weather_raw_df = pd.DataFrame()
                start_date = '2022-04-01'
                end_date = '2023-05-15'
                for station_id in station_list:
                    weather_raw_df = pd.concat([weather_raw_df, get_weather_observations_df_for_station(station_id, start_date, end_date)], ignore_index=True)
                weather_raw_df.to_csv(weather_raw_df_filepath, index=False)
                
            # using weather_station_df and weather_raw_df, create the weather_df. Take an average for each zipcode across the stations
            weather_df_filepath = 'db_dump/data/weather/weather_df.csv'
            if os.path.exists(weather_df_filepath):
                weather_df = pd.read_csv(weather_df_filepath, dtype={'zipcode': str})
            else:
                # rename weather_raw_df column: STATION -> station_id
                weather_raw_df = weather_raw_df.rename(columns={'STATION': 'station_id', 'DATE': 'date_str'})
                # add "GHCND:" to the station_id of weather_raw_df
                weather_raw_df['station_id'] = 'GHCND:' + weather_raw_df['station_id']
                # merge weather_raw_df with weather_station_df
                weather_df = pd.merge(weather_raw_df, weather_station_df, on=['station_id'], how='inner')
                weather_df = weather_df[['zipcode', 'date_str', 'TMAX', 'TMIN', 'AWND', 'PRCP']].copy()
                weather_df = weather_df.groupby(['zipcode', 'date_str']).mean().reset_index()
                weather_df.to_csv(weather_df_filepath, index=False)
            
            participants_df = pd.DataFrame(db.participants.find({}, {'_id': 0, 'user_id': 1, 'zipcode': 1}))
            # convert the zipcode to string
            participants_df['zipcode'] = participants_df['zipcode'].astype(str)
            # pad the zipcode with 0s while casting integers to string
            participants_df['zipcode'] = participants_df['zipcode'].apply(lambda x: x.zfill(5))

            weather_df = pd.merge(weather_df, participants_df, on=['zipcode'], how='inner')

            # fill the missing AWND and PRCP with 0
            weather_df['AWND'] = weather_df['AWND'].fillna(0)
            weather_df['PRCP'] = weather_df['PRCP'].fillna(0)
            
            daily_df = pd.DataFrame(db.daily.find({}, {'_id': 0, 'user_id': 1, 'date_str': 1}))
            daily_df = pd.merge(daily_df, weather_df, on=['user_id', 'date_str'], how='left')

            daily_collection = db['daily']
            daily_collection.bulk_write([
                UpdateOne(
                    {'user_id': row['user_id'], 'date_str': row['date_str']},
                    {'$set': {
                        'tmax': row['TMAX'],
                        'tmin': row['TMIN'],
                        'awnd': row['AWND'],
                        'prcp': row['PRCP']
                    }}
                ) for i, row in daily_df.iterrows()
            ])

def transform_survey():
    if COLLECTION_SURVEY in SETTINGS_REFRESH_COLLECTIONS:
        logging.info(msg="Starting transform_survey()")
        # 1. connect to the database
        # create a client instance of the MongoClient class
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

        # 2. get participant_list
        logging.info(msg="Fetching the participant list")
        participant_list = get_participant_list()

        # 3. fetch the survey_survey collection
        logging.info(msg="Fetching the notification collection")
        collection_name = 'surveys_survey'
        collection = db[collection_name]
        survey_df = pd.DataFrame(collection.find({'user_id': {'$in': participant_list}}, {'_id': 0, 'uuid': 1, 'user_id': 1, 'created': 1}))
        survey_df.rename(columns={'uuid': 'survey_id', 'created': 'when_asked'}, inplace=True)
        survey_df['when_asked'] = pd.to_datetime(survey_df['when_asked']).dt.tz_convert('America/Los_Angeles')
        survey_df['when_asked_date_str'] = survey_df['when_asked'].dt.strftime('%Y-%m-%d')
        survey_df['when_asked_time_str'] = survey_df['when_asked'].dt.strftime('%H:%M:%S')
        df_info(survey_df, 'survey_df')
        survey_id_list = survey_df['survey_id'].unique().tolist()
        logging.debug(msg="survey_id_list[:10]: \n{}".format(survey_id_list[:10]))

        # 4. fetch the survey_surveyquestion collection
        logging.info(msg="Fetching the survey_surveyquestion collection")
        collection_name = 'surveys_surveyquestion'
        collection = db[collection_name]
        question_df = pd.DataFrame(collection.find({'survey_id': {'$in': survey_id_list}}, {'_id': 0, 'id': 1, 'name': 1, 'label': 1, 'survey_id': 1, 'order': 1, 'kind': 1}))
        question_df.rename(columns={'id': 'surveyquestion_id', 'name': 'question_name', 'label': 'question_text', 'order': 'question_order'}, inplace=True)
        df_info(question_df, name='question_df')
        surveyquestion_id_list = question_df['surveyquestion_id'].unique().tolist()
        logging.debug(msg="surveyquestion_id_list[:10]: \n{}".format(surveyquestion_id_list[:10]))

        # 5. fetch the survey_surveyanswer collection
        logging.info(msg="Fetching the survey_surveyanswer collection")
        collection_name = 'surveys_surveyanswer'
        collection = db[collection_name]
        answer_df = pd.DataFrame(collection.find({'question_id': {'$in': surveyquestion_id_list}}, {'_id': 0, 'id': 1, 'label': 1, 'value': 1, 'order': 1}))
        answer_df.rename(columns={'id': 'surveyanswer_id', 'label': 'answer_text', 'value': 'answer_value', 'order': 'answer_order'}, inplace=True)
        df_info(answer_df, name='answer_df')


        # 6. fetch the survey_surveyresponse collection
        logging.info(msg="Fetching the survey_surveyresponse collection")
        collection_name = 'surveys_surveyresponse'
        collection = db[collection_name]
        response_df = pd.DataFrame(collection.find({'survey_id': {'$in': survey_id_list}}, {'_id': 0, 'id': 1, 'user_id': 1, 'question_id': 1, 'answer_id': 1}))
        response_df.rename(columns={'id': 'surveyresponse_id', 'question_id': 'surveyquestion_id', 'answer_id': 'surveyanswer_id'}, inplace=True)
        df_info(response_df, name='response_df')
        
        # 7. merge the dataframes
        logging.info(msg="Merging the dataframes")
        logging.info(msg="survey_df.shape: {}".format(survey_df.shape))
        logging.info(msg="question_df.shape: {}".format(question_df.shape))
        logging.info(msg="answer_df.shape: {}".format(answer_df.shape))
        logging.info(msg="response_df.shape: {}".format(response_df.shape))

        logging.debug(msg="survey_df.columns: {}".format(survey_df.columns))
        logging.debug(msg="question_df.columns: {}".format(question_df.columns))
        survey_df = survey_df.merge(question_df, on='survey_id', how='left')

        logging.debug(msg="survey_df.columns: {}".format(survey_df.columns))
        logging.debug(msg="response_df.columns: {}".format(response_df.columns))
        survey_df = survey_df.merge(response_df, on='surveyquestion_id', how='left')

        logging.debug(msg="survey_df.columns: {}".format(survey_df.columns))
        logging.debug(msg="answer_df.columns: {}".format(answer_df.columns))
        survey_df = survey_df.merge(answer_df, on='surveyanswer_id', how='left')

        df_info(survey_df, name='survey_df')
        
        # 8. Organize the message table data
        logging.info(msg="Organizing the message table data")
        message_collection = db['push_messages_message']
        message_df = pd.DataFrame(message_collection.find({'recipient_id': {'$in': participant_list}}, {'_id': 0, 'id': 1, 'uuid': 1, 'created': 1, 'device_id': 1, 'recipient_id': 1, 'external_id':1, 'body': 1, 'data': 1, 'collapse_subject': 1}))

        # 8.1. rename the columns
        message_df.rename(columns={'id': 'message_id', 'created': 'when_sent', 'recipient_id': 'user_id', 'body': 'message_text', 'data': 'message_json', 'collapse_subject': 'message_type'}, inplace=True)

        # 8.2. parse the message_json column
        # 8.2.1. remove the row with NaNs in message_json column
        message_df = message_df[message_df['message_json'].notna()]
        # 8.2.2. convert the message_json column to json
        message_df['message_json'] = message_df['message_json'].apply(lambda x: json.loads(x))
        # 8.2.3. create a new column for survey
        message_df['survey_json'] = message_df['message_json'].apply(lambda x: x['survey'])
        message_df = message_df[message_df['survey_json'].notna()]
        message_df['survey_json'] = message_df['survey_json'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        message_df['survey_id'] = message_df['survey_json'].apply(lambda x: x['id'])

        # 8.2.4. remove the message_json column
        message_df.drop(columns=['message_json', 'survey_json'], inplace=True)


        # 8.3. fetch message_receipt collection
        messagereceipt_collection = db['push_messages_messagereceipt']

        # 8.3.1. fetch the message_receipt collection
        messagereceipt_df = pd.DataFrame(messagereceipt_collection.find({'message_id': {'$in': message_df['message_id'].tolist()}}, {'_id': 0, 'message_id': 1, 'type': 1, 'time': 1}))

        # 8.3.2. use the list of types, and make a wide-dataframe from the long-dataframe of messagereceipt_df for the earliest times
        col_order = ['sent', 'onesignal-sent', 'received', 'opened', 'engaged', 'failed']
        messagereceipt_df = messagereceipt_df[messagereceipt_df['type'].isin(col_order)]
        messagereceipt_df = messagereceipt_df.sort_values(by=['message_id', 'time'])
        messagereceipt_df = messagereceipt_df.groupby(['message_id', 'type']).first().reset_index()
        messagereceipt_df = messagereceipt_df.pivot(index='message_id', columns='type', values='time')
        messagereceipt_df = messagereceipt_df[col_order]
        messagereceipt_df.columns.name = None
        messagereceipt_df.reset_index(inplace=True)

        # 8.3.3. join with the message_df
        message_df = message_df.merge(messagereceipt_df, on='message_id', how='left')


        # 8.4. pageview collection
        pageview_collection = db['page_views_pageview']

        # 8.4.1. fetch the pageview collection
        pageview_df = pd.DataFrame(pageview_collection.find({"uri": {"$regex": "^/notification"}}, {'_id': 0, 'uri': 1, 'time': 1, 'created': 1, 'user_id': 1}))

        # 8.4.2. rename the columns
        pageview_df.rename(columns={'time': 'pageview_when_viewed', 'created': 'pageview_when_logged'}, inplace=True)

        # 8.4.3. parse the uri column to get the message_id. example: "/notification/dfbbc49a-6fef-4907-ac31-6f51bc20eed6"
        pageview_df['uuid'] = pageview_df['uri'].apply(lambda x: x.split('/')[-1])

        # 8.4.4. remove the uri column
        pageview_df.drop(columns=['uri'], inplace=True)

        # 8.4.5. join with the message_df
        message_df = message_df.merge(pageview_df, on=['user_id', 'uuid'], how='left')

        # 8.5. merge the survey_df with message_df
        logging.info(msg="Merging the survey_df with message_df")
        logging.info(msg="survey_df.shape: {}".format(survey_df.shape))
        logging.info(msg="message_df.shape: {}".format(message_df.shape))
        survey_df = survey_df.merge(message_df, on=['user_id', 'survey_id'], how='left')
        logging.info(msg="survey_df.shape: {}".format(survey_df.shape))

        # 9. merge the redundant rows
        # 9.1. if more than one survey with the same user_id and question_text were asked (with respect to `when_asked` column) within a minute between them, then merge the rows. The merging logic is as follows.        
        #      if one of them has answer_text, then use that answer_text. delete other rows in the group.
        #      if more than one of them has answer_text, then use the first one. delete other rows in the group.
        #      if none of them has answer_text, then look at the pageview_when_viewed column. 
        #              if one of them has pageview_when_viewed as non-null, then use that row. delete other rows in the group.
        #              if more than one of them has pageview_when_viewed as non-null, then use the first one. delete other rows in the group.
        #              if none of them has pageview_when_viewed as non-null, then look at the opened column. 
        #                       if one of them has opened as non-null, then use that row. delete other rows in the group.
        #                       if more than one of them has opened as non-null, then use the first one. delete other rows in the group.
        #                       if none of them has opened as non-null, then look at the received column.
        #                               if one of them has received as non-null, then use that row. delete other rows in the group.
        #                               if more than one of them has received as non-null, then use the first one. delete other rows in the group.
        #                               if none of them has received as non-null, then look at the sent column.
        #                                       if one of them has sent as non-null, then use that row. delete other rows in the group.
        #                                       if more than one of them has sent as non-null, then use the first one. delete other rows in the group.
        #                                       if none of them has sent as non-null, then look at the when_asked column.
        #                                               if one of them has when_asked as non-null, then use that row. delete other rows in the group.
        #                                               if more than one of them has when_asked as non-null, then use the first one. delete other rows in the group.
        #                                               if none of them has when_asked as non-null, then use the first one. delete other rows in the group.

        logging.info(msg="Merging the redundant rows")
        logging.info(msg="survey_df.shape: {}".format(survey_df.shape))
        survey_df = survey_df.sort_values(by=['user_id', 'question_text', 'when_asked'])
        survey_df['when_asked'] = pd.to_datetime(survey_df['when_asked']).dt.tz_convert('America/Los_Angeles')
        
        # 9.2. calculate the time difference between the current row and the previous row within the same user_id and question_text
        survey_df['when_asked_diff'] = survey_df.groupby(['user_id', 'question_text'])['when_asked'].diff()
        survey_df['when_asked_diff'] = survey_df['when_asked_diff'].fillna(pd.Timedelta(seconds=9999))
        survey_df['when_asked_diff'] = survey_df['when_asked_diff'].apply(lambda x: x.total_seconds())
        survey_df['when_asked_diff'] = survey_df['when_asked_diff'].astype(int)
        logging.debug(msg="survey_df['when_asked_diff'].value_counts(): \n{}".format(survey_df['when_asked_diff'].value_counts()))

        # 9.3. if the time difference is less than 60 seconds, then merge the rows
        survey_df['when_asked_diff'] = survey_df['when_asked_diff'].apply(lambda x: 0 if x < 60 else 1)

        # 9.4. if the time difference is 0, then give the row a group number
        survey_df['group_id'] = survey_df['when_asked_diff'].cumsum()

        # 9.5. create a group size column to see how many rows are in each group
        survey_df['group_size'] = survey_df.groupby(['user_id', 'question_text', 'group_id'])['group_id'].transform('size')

        # 9.5. for the merging, sort the dataframe by answer_text, pageview_when_viewed, opened, received, sent, when_asked
        survey_df = survey_df.sort_values(by=['answer_text', 'pageview_when_viewed', 'opened', 'received', 'sent', 'when_asked'])

        # 9.6. follow the logic.
        def pick_one_row(group_df, col_name):
            if group_df.shape[0] == 1:
                return group_df
            indices = group_df[col_name].notna()
            non_na_df = group_df[indices]
            count = non_na_df.shape[0]
            if count == 1:
                return non_na_df
            else:
                return group_df
        
        logging.info(msg="survey_df.shape: {}".format(survey_df.shape))
        col_name_list = [
            'answer_text', 'pageview_when_viewed', 'opened', 'received', 'sent', 'when_asked'
        ]

        for col_name in col_name_list:
            # separate out for the rows with group_size > 1
            logging.info(msg="Separating out for the rows with group_size > 1. col_name: {}".format(col_name))
            group_df = survey_df[survey_df['group_size'] > 1]
            logging.info(msg="group_df.shape: {}".format(group_df.shape))

            # prepare the ray objects vector
            logging.info(msg="Merging the rows with the same user_id, question_text, and group_id. col_name: {}".format(col_name))
            group_df = group_df.groupby(['user_id', 'question_text', 'group_id']).apply(lambda x: pick_one_row(x, col_name))
            logging.info(msg="group_df.shape: {}".format(group_df.shape))

            # merge the group_df with the survey_df
            survey_df = pd.concat([survey_df[survey_df['group_size'] == 1], group_df], ignore_index=True)
            logging.info(msg="survey_df.shape: {}".format(survey_df.shape))

            # update the group_size column
            survey_df['group_size'] = survey_df.groupby(['user_id', 'question_text', 'group_id'])['group_id'].transform('size')
            logging.info(msg="survey_df.shape: {}".format(survey_df.shape))

        def pick_first_row(group_df):
            return group_df.iloc[0]
        
        logging.info(msg="Merging the rows with the same user_id, question_text, and group_id. col_name: {}".format(col_name))
        group_df = survey_df[survey_df['group_size'] > 1]
        logging.info(msg="group_df.shape: {}".format(group_df.shape))
        group_df = group_df.groupby(['user_id', 'question_text', 'group_id']).apply(lambda x: pick_first_row(x))        
        logging.info(msg="survey_df.shape: {}".format(survey_df.shape))
        survey_df = pd.concat([survey_df[survey_df['group_size'] == 1], group_df], ignore_index=True)

        # update the group_size column
        survey_df['group_size'] = survey_df.groupby(['user_id', 'question_text', 'group_id'])['group_id'].transform('size')
        logging.info(msg="survey_df.shape: {}".format(survey_df.shape))


        # 8. reorder the columns
        logging.info(msg="Reordering the columns")
        survey_df = survey_df[[
            'user_id', 'when_asked', 'when_asked_date_str', 'when_asked_time_str', 
            'question_name', 'question_text', 'question_order',
            'answer_text', 'answer_value', 'answer_order', 'kind', 
            'survey_id', 'surveyquestion_id', 'surveyanswer_id', 'surveyresponse_id', 
            'when_sent', 'received', 'opened', 'engaged', 'pageview_when_viewed']]
        
        # 9. convert string datetime columns to datetime
        logging.info(msg="Converting string datetime columns to datetime")

        time_cols = ['when_sent', 'received', 'opened', 'engaged', 'pageview_when_viewed']

        def timediff(row):
            for time_column in time_cols:
                if pd.isnull(row[time_column]):
                    continue
                elif isinstance(row[time_column], str):
                    row[time_column] = (dateparse(row[time_column]) - row['when_asked']).total_seconds()
                else:
                    row[time_column] = (row[time_column] - row['when_asked']).total_seconds()
            return row

        survey_df = survey_df.apply(timediff, axis=1)

        # 10. save the dataframe to the database
        logging.info(msg="Saving the dataframe to the database")
        collection_name = 'survey'
        collection = tdb[collection_name]
        collection.delete_many({})
        collection.insert_many(survey_df.to_dict('records'))
        logging.info(msg="Finished refresh_survey()")

def select_daily_ema():
    if COLLECTION_SURVEY_DAILY_EMA in SETTINGS_REFRESH_COLLECTIONS:
        logging.info(msg="Starting select_daily_ema()")
        # 1. connect to the database
        # create a client instance of the MongoClient class
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)
        collection_name = 'survey'

        # 2. fetch the survey collection
        logging.info(msg="Fetching the survey collection")
        collection = tdb[collection_name]
        survey_df = pd.DataFrame(collection.find({}, {'_id': 0}))
        df_info(survey_df, name='survey_df')
        
        # 3. select the daily ema questions
        logging.info(msg="Selecting the daily ema questions")
        survey_df = survey_df[survey_df['question_name'].str.contains('daily_ema', na=False)]
        df_info(survey_df, name='survey_df')
        
        # 4. assign the construct names
        logging.info(msg="Assigning the construct names")

        # 4.1. create a dictionary of construct names
        construct_dict = {
            'Being active is a <b>top priority</b> tomorrow. ': 'C3',
            '<b>Circumstances will help me</b> to be active tomorrow (e.g., nice weather, getting in nature, free time).': 'C4',
            'My <b>schedule makes it easy</b> to be active tomorrow.': 'C5',
            'I <b>expect obstacles</b> (e.g., no time, unsafe, poor weather) to being active tomorrow.': 'C6',
            'I know how to <b>solve any problems</b> to being active tomorrow.': 'C7',
            'I am confident I can <b>overcome obstacles</b> to being active tomorrow.': 'C8',
            "<b>No matter what</b>, I'm going to be active tomorrow.": 'C9',
            'In general, my <b>friends help me</b> to be active.': 'D1',
            'I regularly feel <b>urges to</b> be active.': 'D2',
            'I am active because it <b>helps me feel better</b> (e.g., reduce stress, stiffness, or fatigue).': 'D3',
            'I have a <b>wide range of strategies</b> (e.g., call friends while walking) that I use to be active regularly. ': 'D4',
            'My <b>typical Monday includes being active.</b>': 'E1_1',
            'My <b>typical Tuesday includes being active.</b>': 'E1_2',
            'My <b>typical Wednesday includes being active.</b>': 'E1_3',
            'My <b>typical Thursday includes being active.</b>': 'E1_4',
            'My <b>typical Friday includes being active.</b>': 'E1_5',
            'My <b>typical Saturday includes being active.</b>': 'E1_6',
            'My <b>typical Sunday includes being active.</b>': 'E1_7'
        }

        # 4.2. add the construct names to the dataframe
        survey_df['construct_name'] = survey_df['question_text'].map(construct_dict)

        # 4. save the dataframe to the database
        logging.info(msg="Saving the dataframe to the database")
        collection_name = COLLECTION_SURVEY_DAILY_EMA
        collection = tdb[collection_name]
        collection.delete_many({})
        collection.insert_many(survey_df.to_dict('records'))
        logging.info(msg="Finished select_daily_ema()")

def widen_daily_ema():
    if COLLECTION_SURVEY_DAILY_EMA in SETTINGS_REFRESH_COLLECTIONS:
        logging.info(msg="Starting widen_daily_ema()")
        # 1. connect to the database
        # create a client instance of the MongoClient class
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)
        collection_name = COLLECTION_SURVEY_DAILY_EMA

        # 2. fetch the survey collection
        logging.info(msg="Fetching the survey_daily_ema collection")
        collection = tdb[collection_name]
        survey_df = pd.DataFrame(collection.find({}, {'_id': 0}))
        df_info(survey_df, name='survey_df')

        # 2.1. check the redundant rows
        logging.info(msg="Checking the redundant rows")
        redundant_rows = survey_df[survey_df.duplicated(subset=['survey_id', 'construct_name'], keep=False)]
        logging.info(msg="redundant_rows.shape: {}".format(redundant_rows.shape))
        logging.debug(msg="redundant_rows.head(): \n{}".format(redundant_rows[['survey_id', 'question_text', 'surveyanswer_id', 'answer_value']].head()))

        # 2.2. sort the survey_df, then use the last row for the redundant rows
        logging.info(msg="Using the last row for the redundant rows")
        survey_df = survey_df.sort_values(by=['survey_id', 'construct_name', 'when_asked'], ascending=[True, True, True])
        survey_df = survey_df.drop_duplicates(subset=['survey_id', 'construct_name'], keep='last')
        
        # 3. pivot the dataframe
        logging.info(msg="Pivoting the dataframe")
        survey_wide_df = survey_df.pivot(index='survey_id', columns='construct_name', values='answer_value')
        df_info(survey_wide_df, name='survey_wide_df')

        # 4. select the survey info
        logging.info(msg="Selecting the survey info")
        survey_info_df = survey_df[['survey_id', 'user_id', 'when_asked', 'when_asked_date_str', 'when_asked_time_str', 'kind']]
        survey_info_df = survey_info_df.drop_duplicates()
        df_info(survey_info_df, name='survey_info_df')

        # 5. merge the survey info with the wide survey
        logging.info(msg="Merging the survey info with the wide survey")
        survey_wide_df = survey_info_df.merge(survey_wide_df, on='survey_id', how='left')
        df_info(survey_wide_df, name='survey_wide_df')
        
        # 6. if the answer value is NaN for all the constructs ranging C3 to C9, D1 to D4, E1_1 to E1_7, then mark it as unanswered. If there is at least one answer_value, then mark it as answered.
        logging.info(msg="Marking the unanswered surveys")
        survey_wide_df['answered'] = survey_wide_df.apply(lambda x: False if x[['C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'D1', 'D2', 'D3', 'D4', 'E1_1', 'E1_2', 'E1_3', 'E1_4', 'E1_5', 'E1_6', 'E1_7']].isnull().all() else True, axis=1)

        # 7. calculate the elapsed_since_last_survey for each user
        logging.info(msg="Using the last answered survey")
        survey_wide_df = survey_wide_df.sort_values(by=['user_id', 'when_asked'], ascending=[True, True])
        survey_wide_df['when_asked'] = survey_wide_df['when_asked'].astype('datetime64[ns]')
        survey_wide_df['elapsed_since_last_survey'] = survey_wide_df.groupby('user_id')['when_asked'].diff().dt.total_seconds()

        # 8. give the cluster id incrementally. But if the elapsed_since_last_survey is less than 3600 seconds, then give the same cluster id as the previous survey.
        logging.info(msg="Giving the cluster id incrementally")
        survey_wide_df['cluster_id'] = survey_wide_df.groupby('user_id', group_keys=False)['elapsed_since_last_survey'].apply(lambda x: x.gt(3600).cumsum())
        survey_wide_df['cluster_id'] = survey_wide_df['cluster_id'].astype('int')

        # 9. in the cluster, if there is one survey, use it. if there are more than one surveys, and the last survey is answered, use it. if there are more than one surveys, and the last survey is unanswered, use the last answered survey.
        logging.info(msg="Using the last answered survey")
        survey_wide_df = survey_wide_df.sort_values(by=['user_id', 'cluster_id', 'answered', 'when_asked'], ascending=[True, True, True, True])
        survey_wide_df = survey_wide_df.drop_duplicates(subset=['user_id', 'cluster_id'], keep='last')

        # 10. recalculate the elapsed_since_last_survey for each user
        logging.info(msg="Recalculating the elapsed_since_last_survey")
        survey_wide_df = survey_wide_df.sort_values(by=['user_id', 'when_asked'], ascending=[True, True])
        survey_wide_df['when_asked'] = survey_wide_df['when_asked'].astype('datetime64[ns]')
        survey_wide_df['elapsed_since_last_survey'] = survey_wide_df.groupby('user_id')['when_asked'].diff().dt.total_seconds()
        survey_wide_df.drop(columns=['cluster_id'], inplace=True)

        # 7. save the dataframe to the database
        logging.info(msg="Saving the dataframe to the database")
        collection.delete_many({})
        collection.insert_many(survey_wide_df.to_dict('records'))
        logging.info(msg="Finished widen_daily_ema()")

def copy_daily_ema():
    if COLLECTION_SURVEY_DAILY_EMA in SETTINGS_REFRESH_COLLECTIONS:
        logging.info(msg="Starting copy_daily_ema()")
        # 1. connect to the database
        # create a client instance of the MongoClient class
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)
        collection_name = COLLECTION_SURVEY_DAILY_EMA
        
        # 2. fetch the current daily_ema collection
        logging.info(msg="Fetching the current COLLECTION_SURVEY_DAILY_EMA collection")
        daily_ema_collection = tdb[collection_name]
        daily_ema_df = pd.DataFrame(daily_ema_collection.find({}, {
            '_id': 0, 
            'user_id': 1,
            'when_asked_date_str': 1,
            'C3': 1,
            'C4': 1,
            'C5': 1,
            'C6': 1,
            'C7': 1,
            'C8': 1,
            'C9': 1,
            'D1': 1,
            'D2': 1,
            'D3': 1,
            'D4': 1,
            'E1_1': 1,
            'E1_2': 1,
            'E1_3': 1,
            'E1_4': 1,
            'E1_5': 1,
            'E1_6': 1,
            'E1_7': 1,
            'answered': 1,
        }))
        daily_ema_df.rename(columns={'when_asked_date_str': 'date_str', 'answered': 'daily_ema_answered'}, inplace=True)
        
        # 3. save the dataframe to the database
        logging.info(msg="Saving the dataframe to the database")
        collection_name = 'daily'
        collection = tdb[collection_name]
        
        collection.bulk_write([
            UpdateOne(
                filter={'user_id': row['user_id'], 'date_str': row['date_str']},
                update={'$set': row.to_dict()}
            ) for _, row in daily_ema_df.iterrows()
        ])

        logging.info(msg="Finished copy_daily_ema()")

def transform_bout_planning_ema_decision():
    if COLLECTION_SURVEY_BOUT_PLANNING_EMA in SETTINGS_REFRESH_COLLECTIONS:
        logging.info(msg="Starting transform_bout_planning_ema_decision()")
        # 1. connect to the database
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

        # 2. load the BPN decision data
        logging.info(msg="Loading the BPN decision data")

        # 2.1. load participant list
        participant_list = get_participant_list()

        # 2.2. load the BPN decision data
        collection_name = 'bout_planning_notification_boutplanningdecision'
        collection = db[collection_name]
        bpn_decision_df = pd.DataFrame(collection.find({
            'user_id': {'$in': participant_list},
        }, {
            '_id': 0,
            'data': 0,
        }))
        bpn_decision_df.rename(columns={'id': 'decision_id'}, inplace=True)
        df_info(bpn_decision_df, 'bpn_decision_df')
        
        # 2.3. load the BPN survey data
        collection_name = 'bout_planning_notification_boutplanningnotification'
        collection = db[collection_name]
        bpn_survey_df = pd.DataFrame(collection.find({
            'user_id': {'$in': participant_list},
            'decision_id': {'$ne': None}
        }, {
            '_id': 0,
            'when': 0,
            'level_id': 0,
        }))
        bpn_survey_df.rename(columns={'id': 'survey_id'}, inplace=True)
        df_info(bpn_survey_df, name='bpn_survey_df')

        # 2.4 load days_day collection
        collection_name = 'days_day'
        collection = db[collection_name]
        days_day_df = pd.DataFrame(collection.find({
            'user_id': {'$in': participant_list},
        }, {
            '_id': 0
        }))
        days_day_df['start'] = pd.to_datetime(days_day_df['start'])
        days_day_df['end'] = pd.to_datetime(days_day_df['end'])

        # 2.5. sort the days_day_df by user_id and start
        days_day_df.sort_values(by=['user_id', 'start'], inplace=True)
        df_info(days_day_df, name='days_day_df')        

        # 2.6. infer local time
        @ray.remote
        def infer_local_time(utc_datetime, user_id):
            days_day_df_user = days_day_df[days_day_df['user_id'] == user_id]
            utc_datetime = pd.to_datetime(utc_datetime)
            for _, row in days_day_df_user.iterrows():
                start_dt = row['start']
                end_dt = row['end']
                if start_dt <= utc_datetime <= end_dt:
                    return utc_datetime.replace(tzinfo=pytz.utc).astimezone(tz=row['timezone'])
            return utc_datetime.replace(tzinfo=pytz.utc).astimezone(tz="America/Los_Angeles")

        df_info(bpn_decision_df, name='bpn_decision_df')

        # 2.7. sort the bpn_decision_df by user_id and when_created
        user_id_when_created_df = bpn_decision_df[['user_id', 'when_created']].copy()
        user_id_when_created_df.sort_values(by=['user_id', 'when_created'], inplace=True)

        # 2.8. infer local time
        logging.info(msg="Constructing future list of local time inference")
        future_list = []
        for i, row in user_id_when_created_df.iterrows():
            future_list.append(infer_local_time.remote(row['when_created'], row['user_id']))

        # 2.9. get the local time list
        logging.info(msg="Finished constructing future list of local time inference. Starting inferring local time")
        local_time_list = ray.get(future_list)
        logging.info(msg="Finished inferring local time")
        
        # 2.10. add the local time list to the user_id_when_created_df
        user_id_when_created_df['when_created_local'] = local_time_list
        df_info(user_id_when_created_df, name='user_id_when_created_df')

        # 2.11. merge the user_id_when_created_df with bpn_decision_df
        logging.info(msg="Merging user_id_when_created_df with bpn_decision_df on user_id and when_created")
        logging.debug(msg="bpn_decision_df.shape: {}, user_id_when_created_df.shape: {}".format(bpn_decision_df.shape, user_id_when_created_df.shape))
        logging.debug(msg="bpn_decision_df.columns: {}, user_id_when_created_df.columns: {}".format(bpn_decision_df.columns, user_id_when_created_df.columns))
        bpn_decision_df = pd.merge(bpn_decision_df, user_id_when_created_df, on=['user_id', 'when_created'])
        df_info(bpn_decision_df, name='bpn_decision_df')

        # 2.12. drop the when_created column
        logging.info(msg="Dropping the when_created column")
        bpn_decision_df.drop(columns=['when_created'], inplace=True)
        df_info(bpn_decision_df, name='bpn_decision_df')

        # 2.13. join the BPN decision data with the BPN survey data
        bpn_decision_df = pd.merge(bpn_decision_df, bpn_survey_df, on=['user_id', 'decision_id'], how='left')
        df_info(bpn_decision_df, name='bpn_decision_df')

        # 2.14. cast when_created_local to str
        logging.info(msg="Casting when_created_local to str")
        bpn_decision_df['when_created_local_str'] = bpn_decision_df['when_created_local'].astype(str)
        df_info(bpn_decision_df, name='bpn_decision_df')

        # 2.15. cast when_created_local_str to datetime
        bpn_decision_df['when_created_local_dt'] = pd.to_datetime(bpn_decision_df['when_created_local_str'], format="mixed")
        df_info(bpn_decision_df, name='bpn_decision_df')

        # 2.16. cast the when_created_local_dt column to date_str column
        bpn_decision_df['date_str'] = bpn_decision_df['when_created_local_dt'].apply(lambda x: x.date().strftime('%Y-%m-%d'))
        df_info(bpn_decision_df, name='bpn_decision_df')

        # 2.17. quantize when_created column to each hour
        # Assuming your dataframe is called bpn_decision_df and has a 'when_created' column with datetime objects
        bpn_decision_df['when_created_local_dt'] = bpn_decision_df['when_created_local_dt'].apply(lambda x: x.replace(minute=0, second=0, microsecond=0))
        df_info(bpn_decision_df, name='bpn_decision_df')

        # 2.18. cast the when_created column to time_str column
        bpn_decision_df['time_str'] = bpn_decision_df['when_created_local_dt'].apply(lambda x: x.time().strftime('%H:%M'))
        df_info(bpn_decision_df, name='bpn_decision_df')

        # 2.19. calculate local hour of day
        bpn_decision_df['hour_of_day'] = bpn_decision_df['when_created_local_dt'].apply(lambda x: x.hour)
        
        # 2.20. group by user_id, date_str, hour_of_day, then count the number of decisions in each group
        bpn_decision_df['num_decisions'] = bpn_decision_df.groupby(['user_id', 'date_str', 'hour_of_day'])['decision_id'].transform('count')

        # 2.23. calculate decision point index (0-based)
        bpn_decision_df['decision_point_index'] = bpn_decision_df.groupby(['user_id', 'date_str']).cumcount()

        # 2.24. drop the when_created_local column
        logging.info(msg="Dropping the when_created_local column")
        bpn_decision_df.drop(columns=['when_created_local'], inplace=True)
        df_info(bpn_decision_df, name='bpn_decision_df', save=True)

        # 2.99 load the BPN survey data
        collection_name = COLLECTION_SURVEY_BOUT_PLANNING_EMA
        collection = tdb[collection_name]

        collection.delete_many(filter={})
        collection.insert_many(bpn_decision_df.to_dict('records'))

        

def select_bout_planning_ema():
    if COLLECTION_SURVEY_BOUT_PLANNING_EMA in SETTINGS_REFRESH_COLLECTIONS:
        logging.info(msg="Starting select_bout_planning_ema()")
        # 1. connect to the database
        # create a client instance of the MongoClient class
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)
        collection_name = COLLECTION_SURVEY_BOUT_PLANNING_EMA
        
        # 2. Fetching the current COLLECTION_SURVEY_BOUT_PLANNING_EMA survey documents from COLLECTION_SURVEY
        logging.info(msg="Fetching the current COLLECTION_SURVEY_BOUT_PLANNING_EMA survey documents from COLLECTION_SURVEY")
        
        # 2.1. Get the participant id list
        participant_list = get_participant_list()
        
        # 2.2. Get the survey documents
        # BPN = Bout Planning Survey
        survey_collection = tdb[COLLECTION_SURVEY]
        bpn_survey_df = pd.DataFrame(survey_collection.find({
            'question_name': 'Bout Planning Survey',
            'user_id': {'$in': participant_list}
        }, {'_id': 0}))
        df_info(bpn_survey_df, name='bpn_survey_df')
        bpn_survey_min_df = bpn_survey_df[['user_id', 'survey_id', 'when_asked']].copy()
        
        # 3. Find the corresponding BPN decision documents from COLLECTION_SURVEY_BOUT_PLANNING
        logging.info(msg="Finding the corresponding BPN decision documents from COLLECTION_SURVEY_BOUT_PLANNING")
        bpn_decision_collection = tdb[COLLECTION_SURVEY_BOUT_PLANNING_EMA]
        bpn_decision_df = pd.DataFrame(bpn_decision_collection.find({
            'user_id': {'$in': participant_list},
            'return_bool': {'$in': ['t', 'f']}
        }, {'_id': 0}))
        df_info(bpn_decision_df, name='bpn_decision_df')

        # 3.2. for the decision rows with 't', find the corresponding survey row
        logging.info(msg="Finding the corresponding survey row for the decision rows with 't'")
        bpn_decision_t_df = bpn_decision_df[bpn_decision_df['return_bool'] == 't']

        def find_next_message(row, survey_df):
            user_id = row['user_id']
            when_created_local_dt = row['when_created_local_dt']
            survey_df_user = survey_df[survey_df['user_id'] == user_id]
            survey_df_user = survey_df_user[survey_df_user['when_asked'] > when_created_local_dt]
            survey_df_user = survey_df_user.sort_values(by=['when_asked'], ascending=[True])

            if survey_df_user.shape[0] > 0:
                next_survey_when_asked = survey_df_user.iloc[0]['when_asked']
                time_diff = (next_survey_when_asked - when_created_local_dt).total_seconds()
                if time_diff < 90 * 60: # it allows the notifications to be sent within 90 minutes
                    return survey_df_user.iloc[0]['survey_id']
                else:
                    return None
            else:
                return None

        bpn_decision_t_df['survey_uuid'] = bpn_decision_t_df.apply(lambda x: find_next_message(x, bpn_survey_min_df), axis=1)

        # copy the survey_uuid to the bpn_decision_df
        bpn_decision_df = pd.merge(bpn_decision_df, bpn_decision_t_df[['user_id', 'when_created_local_dt', 'survey_uuid']], on=['user_id', 'when_created_local_dt'], how='left')
        
        # 3.6. join the next_survey_id column to the bpn_decision_df
        logging.info(msg="Joining the next_survey_id column to the bpn_decision_df")   
        bpn_survey_df.rename(columns={'survey_id': 'survey_uuid'}, inplace=True) 

        bpn_decision_df = pd.merge(bpn_decision_df, bpn_survey_df, on=['survey_uuid', 'user_id'], how='left')
        logging.info(msg="bpn_decision_df.shape: {}".format(bpn_decision_df.shape))
        logging.debug(msg="bpn_decision_df.head(): \n{}".format(bpn_decision_df.head()))

        # 3.7. remove the decisions caused by the system error
        logging.info(msg="Removing the decisions caused by the system error")

        # 3.7.1. calculate the time difference between the when_created_local_dt and the one before it
        logging.info(msg="Calculating the time difference between the when_created_local_dt and the one before it")
        bpn_decision_df.sort_values(by=['user_id', 'when_created_local_dt'], ascending=[True, True], inplace=True)
        bpn_decision_df['time_diff'] = bpn_decision_df.groupby('user_id')['when_created_local_dt'].diff().dt.total_seconds()
        df_info(bpn_decision_df, name='bpn_decision_df')

        # 3.7.2. group by user_id, then give the group id if the time_diff is greater than 90 minutes
        logging.info(msg="Grouping by user_id, then give the group id if the time_diff is greater than 90 minutes")
        bpn_decision_df['is_new_group'] = bpn_decision_df.groupby('user_id')['time_diff'].transform(lambda x: x > 90 * 60)
        bpn_decision_df['group_id'] = bpn_decision_df.groupby('user_id')['is_new_group'].cumsum()
        bpn_decision_df['group_size'] = bpn_decision_df.groupby(['user_id', 'group_id'])['group_id'].transform('count')
        df_info(bpn_decision_df, name='bpn_decision_df')

        # 3.7.3. remove the decisions caused by the system error
        logging.info(msg="Removing the decisions caused by the system error")
        def pick_one_row(group_df):
            total_count = group_df.shape[0]

            viewed_count = group_df[group_df['pageview_when_viewed'].notnull()].shape[0]
            sent_count = group_df[group_df['when_sent'].notnull()].shape[0]

            if viewed_count == 1:
                return group_df[group_df['pageview_when_viewed'].notnull()].iloc[0]
            elif viewed_count > 1:
                if sent_count == 1:
                    return group_df[group_df['when_sent'].notnull()].iloc[0]
                else:
                    return group_df[group_df['when_sent'].notnull()].iloc[0]
            else:
                return group_df.iloc[0]
        
        bpn_decision_dup_df = bpn_decision_df[bpn_decision_df['group_size'] > 1]
        bpn_decision_dup_df = bpn_decision_dup_df.groupby(['user_id', 'group_id']).apply(pick_one_row)
        bpn_decision_dup_df.reset_index(drop=True, inplace=True)
        df_info(bpn_decision_dup_df, name='bpn_decision_dup_df')

        bpn_decision_df = pd.concat([bpn_decision_df[bpn_decision_df['group_size'] == 1], bpn_decision_dup_df], ignore_index=True)
        df_info(bpn_decision_df, name='bpn_decision_df')

        # 3.7. selecting the columns and rename them
        logging.info(msg="Selecting the columns and rename them")
        bpn_decision_df.rename(columns={
            'when_created_local_dt': 'when_decided_local_dt',
            'when_created_local_str': 'when_decided_local_str',
            'when_asked': 'when_notification_sent_dt',
            'when_asked_date_str': 'when_notification_sent_date_str',
            'when_asked_time_str': 'when_notification_sent_time_str'
        }, inplace=True)
        # bpn_decision_df = bpn_decision_df[[
        #     'user_id', 'survey_id', 
        #     'when_decided_local_dt', 'when_decided_local_str', 'when_notification_sent_dt', 'when_notification_sent_date_str', 'when_notification_sent_time_str', 
        #     'return_bool', 'survey_uuid', 'question_text', 'answer_value'
        #     ]]

        # 3.8. replace NaN with None
        logging.info(msg="Replacing NaN with an empty string")
        bpn_decision_df['when_notification_sent_dt'] = bpn_decision_df['when_notification_sent_dt'].astype(object).where(bpn_decision_df['when_notification_sent_dt'].notnull(), None)
        bpn_decision_df['when_decided_local_dt'] = bpn_decision_df['when_decided_local_dt'].astype(object).where(bpn_decision_df['when_decided_local_dt'].notnull(), None)
        df_info(bpn_decision_df, name='bpn_decision_df')

        # 4. save the dataframe to the database
        logging.info(msg="Saving the dataframe to the database")
        collection = tdb[collection_name]
        collection.delete_many({})
        collection.insert_many(bpn_decision_df.to_dict('records'))
        logging.info(msg="Finished select_bout_planning_ema()")
        

def aggregate_bout_planning_ema():
    if (COLLECTION_DAILY in SETTINGS_REFRESH_COLLECTIONS) and (COLLECTION_SURVEY_BOUT_PLANNING_EMA in SETTINGS_REFRESH_COLLECTIONS):
        logging.info(msg="Starting aggregate_bout_planning_ema()")
        # 1. connect to the database
        # create a client instance of the MongoClient class
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)
        collection_name = COLLECTION_DAILY

        # 2. fetch the current daily collection
        logging.info(msg="Fetching the current daily collection")
        daily_collection = tdb[collection_name]
        daily_df = pd.DataFrame(daily_collection.find({}, {'_id': 0}))
        df_info(daily_df, name='daily_df')

        # 3. fetch the current bout_planning_ema collection
        logging.info(msg="Fetching the current bout_planning_ema collection")
        collection_name = COLLECTION_SURVEY_BOUT_PLANNING_EMA
        bpn_ema_collection = tdb[collection_name]
        bpn_ema_df = pd.DataFrame(bpn_ema_collection.find({}, {'_id': 0}))
        df_info(bpn_ema_df, name='bpn_ema_df')

        # 4. count the total number of bout planning decisions and opened ones per user per day
        # 4.1. filter the bpn_ema_df to only include the rows with return_bool == 't'
        logging.info(msg="Counting the total number of bout planning decisions and opened ones per user per day")
        bpn_ema_df = bpn_ema_df[bpn_ema_df['return_bool'].isin(['t'])]

        # 4.2. group by user_id, date_str, then count the number of decisions in each group
        bpn_ema_df = bpn_ema_df[['user_id', 'date_str', 'opened', 'pageview_when_viewed']]
        bpn_ema_df['sent'] = 1

        # 4.3. mutate the opened column to 1 if opened > 0, otherwise 0
        bpn_ema_df['opened'] = bpn_ema_df['opened'].apply(lambda x: 1 if x > 0 else 0)

        # 4.4. create the viewed column to 1 if pageview_when_viewed is not null, otherwise 0
        bpn_ema_df['viewed'] = bpn_ema_df['pageview_when_viewed'].apply(lambda x: 1 if x is not None else 0)

        # 4.5 remove the pageview_when_viewed column
        bpn_ema_df.drop(columns=['pageview_when_viewed'], inplace=True)

        # 4.6. group by user_id, date_str, then sum the opened and viewed columns
        bpn_ema_df = bpn_ema_df.groupby(['user_id', 'date_str']).sum().reset_index()
        df_info(bpn_ema_df, name='bpn_ema_df')

        # 5. join the bpn_ema_df to the daily_df
        logging.info(msg="Joining the bpn_ema_df to the daily_df")
        daily_df = pd.merge(daily_df, bpn_ema_df, on=['user_id', 'date_str'], how='left')
        df_info(daily_df, name='daily_df')

        # 6. fill the NaNs with 0
        logging.info(msg="Filling the NaNs with 0")
        daily_df['sent'] = daily_df['sent'].fillna(0)
        daily_df['opened'] = daily_df['opened'].fillna(0)
        daily_df['viewed'] = daily_df['viewed'].fillna(0)
        df_info(daily_df, name='daily_df')

        # 6. save the dataframe to the database
        logging.info(msg="Saving the dataframe to the database")
        collection_name = COLLECTION_DAILY
        collection = tdb[collection_name]

        collection.bulk_write([
            UpdateOne(
                {'user_id': row['user_id'], 'date_str': row['date_str']},
                {'$set': {
                    'num_sent': row['sent'],
                    'num_opened': row['opened'],
                    'num_viewed': row['viewed']
                }}
            ) for index, row in daily_df.iterrows()
        ])



        

def transform_message():
    if COLLECTION_MESSAGE in SETTINGS_REFRESH_COLLECTIONS:
        logging.info(msg="Starting transform_message()")
        # 1. connect to the database
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, MONGO_DB_DESTINATION_DBNAME)

        # 2. load the message data
        logging.info(msg="Loading the message data")

        # 2.1. load participant list
        participant_list = get_participant_list()

        # 2.2. load the message data
        collection_name = 'message_message'