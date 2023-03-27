from config import SETTINGS_REFRESH_COLLECTIONS, MONGO_DB_URI_SOURCE, MONGO_DB_URI_DESTINATION
from utils import get_database, build_df_from_collection, extend_df_with_collection, get_participant_list
from constants import *
from tqdm import tqdm
import pandas as pd
import numpy as np
import ray
import logging
import pymongo
from pymongo import UpdateOne

def transform_participants():
    if COLLECTION_PARTICIPANTS in SETTINGS_REFRESH_COLLECTIONS:
        # create a client instance of the MongoClient class
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')

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

        df = extend_df_with_collection(df, db, 'participants_participant', {'cohort_id': cohort_id}, {
            '_id': 0, 'heartsteps_id': 1, 'cohort_id': 1, 'user_id': 1, 'birth_year': 1, 'study_start_date': 1}, on='cohort_id')

        df = df[['heartsteps_id', 'user_id', 'birth_year', 'study_start_date']]
        logging.info("Participants are loaded: {}".format(df.shape[0]))

        participants_collection = tdb['participants']
        participants_collection.insert_many(df.to_dict('records'))
        participant_list = df['user_id'].tolist()

def transform_daily():
    if COLLECTION_DAILY in SETTINGS_REFRESH_COLLECTIONS:
        # create a client instance of the MongoClient class
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')

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
        daily = daily[['user_id', 'date_str', 'level_str']]

        # add a column of day_index per user_id, day_index is the number of days since the study start date from participant collection
        participant_df = pd.DataFrame(tdb[COLLECTION_PARTICIPANTS].find(
            {}, {'_id': 0, 'user_id': 1, 'study_start_date': 1}))
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
        daily['level_int'] = pd.Categorical(
            daily['level_str'], categories=level_categories, ordered=True).codes

        # drop the columns that are not needed
        daily = daily[['user_id', 'date_str', 'date_dt',
                    'day_index', 'level_str', 'level_int']]

        logging.info("Intervention components are loaded: {}".format(daily.shape[0]))
        
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
        daily = pd.merge(daily, temp_goals_df, on=['user_id', 'date_str'], how='right')

        logging.info("Goals are loaded: {}".format(daily.shape[0]))

        # 2.99. insert the data into the database
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

        # create index for user_id and date_str
        if 'user_id_date_str_unique_index' not in daily_collection.index_information():
            logging.info("Create index for user_id and date_str")
            daily_collection.create_index([('user_id', pymongo.ASCENDING), ('date_str', pymongo.ASCENDING)], unique=True, name='user_id_date_str_unique_index', background=True)
    else:
        logging.info("Daily data is already loaded, skip the loading process.")
        
def transform_minute_step():
    if COLLECTION_MINUTE_STEP in SETTINGS_REFRESH_COLLECTIONS:
        # create a client instance of the MongoClient class
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')

        # delete_many participants collection
        logging.debug(msg="Delete all documents in the collection: {}".format(COLLECTION_MINUTE_STEP))
        tdb.minute_step.delete_many({})

        # get the study id list
        logging.debug(msg="Get the study id list")
        participant_list = get_participant_list()

        fitbit_api_account_collection = db['fitbit_api_fitbitaccountuser']

        # 3.1. find the fitbit account for each user_id
        logging.debug(msg="Find the fitbit account for each user_id, and construct the dataframe for the fitbit account")
        fitbit_api_account_df = pd.DataFrame(fitbit_api_account_collection.find(
            {'user_id': {'$in': participant_list}}, {'_id': 0, 'user_id': 1, 'account_id': 1}))
        fitbit_account_id_list = fitbit_api_account_df['account_id'].tolist()
        logging.info("Fitbit accounts are loaded: {}".format(fitbit_api_account_df.shape[0]))
        
        # 4. minute-level steps
        minute_step_collection = db['fitbit_activities_fitbitminutestepcount']
        
        # 4.1. find the minute-level steps from fitbit_activities_fitbitminutestepcount collection for each user_id and minute
        minute_step_df = pd.DataFrame(minute_step_collection.find({'account_id': {
                                    '$in': fitbit_account_id_list}}, {'_id': 0, 'time': 1, 'steps': 1, 'account_id': 1}))

        logging.info("Minute-level steps are loaded: {}".format(minute_step_df.shape[0]))

        # 4.2 merge the minute-level steps with fitbit_api_account_df
        minute_step_df = pd.merge(
            minute_step_df, fitbit_api_account_df, on='account_id', how='left')
        minute_step_df = minute_step_df[['user_id', 'time', 'steps']]
        minute_step_df['time'] = pd.to_datetime(
            minute_step_df['time']).dt.tz_convert('America/Los_Angeles')

        # 4.3 reorganize the minute-level steps to list of integers of each day. insert 0s for missing minutes
        minute_step_df['date_str'] = minute_step_df['time'].dt.strftime('%Y-%m-%d')

        user_id_date_str_groupby = minute_step_df.groupby(['user_id', 'date_str'])
        minute_agg_step_df = pd.DataFrame(columns=['user_id', 'date_str', 'steps'])

        # iterate through each user_id and date with for and pandas applymap
        @ray.remote
        def process_minute_step(user_id, date_str, user_id_date_str_df):
            minutes = [0] * 24 * 60

            for i, row in user_id_date_str_df.iterrows():
                minutes[row['time'].hour * 60 + row['time'].minute] = row['steps']

            return {'user_id': user_id, 'date_str': date_str, 'steps': minutes, 'daily_step_sum': sum(minutes), 'non_zero_minutes': len([x for x in minutes if x > 0])}

        object_storage = {}
        logging.info(msg="Pre-loading the data to process minute steps for {} users".format(len(user_id_date_str_groupby.groups)))
        for user_id, date_str in user_id_date_str_groupby.groups:
            user_id_date_str_df = user_id_date_str_groupby.get_group((user_id, date_str))
            object_storage["{}_{}".format(user_id, date_str)] = ray.put(user_id_date_str_df)

        logging.info(msg="Constructing the future list of ray tasks")
        minute_agg_step_list_future = [
            process_minute_step.remote(user_id, date_str, object_storage["{}_{}".format(user_id, date_str)]) for user_id, date_str in user_id_date_str_groupby.groups
        ]

        logging.info(msg="Waiting for the ray tasks to finish")
        minute_agg_step_list = ray.get(minute_agg_step_list_future)
        logging.info(msg="Finished waiting for the ray tasks to finish. Constructing the pd.DataFrame from the list of dicts.")
        minute_agg_step_df = pd.DataFrame(minute_agg_step_list)
        logging.info(msg="Finished constructing the pd.DataFrame from the list of dicts.")
        logging.debug(msg="minute_agg_step_df: \n{}".format(minute_agg_step_df))

        # 4.4 insert the minute-level steps into the database

        # insert the steps list into the minute_step collection
        logging.info(msg="Inserting the steps list into the minute_step collection")
        minute_step_collection_t = tdb['minute_step']
        minute_step_collection_t.insert_many(minute_agg_step_df.to_dict('records'))
        logging.info(msg="Finished inserting the steps list into the minute_step collection. rows: {}".format(minute_agg_step_df.shape[0]))


def transform_minute_heart_rate():
    collection_name = COLLECTION_MINUTE_HEART_RATE
    if collection_name in SETTINGS_REFRESH_COLLECTIONS:
        # create a client instance of the MongoClient class
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')

        # delete_many participants collection
        logging.debug(msg="Delete all documents in the collection: {}".format(collection_name))
        tdb[collection_name].delete_many({})

        # get the study id list
        logging.debug(msg="Get the study id list")
        participant_list = get_participant_list()

        fitbit_api_account_collection = db['fitbit_api_fitbitaccountuser']

        # 3.1. find the fitbit account for each user_id
        logging.debug(msg="Find the fitbit account for each user_id, and construct the dataframe for the fitbit account")
        fitbit_api_account_df = pd.DataFrame(fitbit_api_account_collection.find(
            {'user_id': {'$in': participant_list}}, {'_id': 0, 'user_id': 1, 'account_id': 1}))
        fitbit_account_id_list = fitbit_api_account_df['account_id'].tolist()
        logging.info("Fitbit accounts are loaded: {}".format(fitbit_api_account_df.shape[0]))
        
        # 4. minute-level steps
        minute_heart_rate_collection = db['fitbit_activities_fitbitminuteheartrate']
        
        # 4.1. find the minute-level steps from fitbit_activities_fitbitminuteheartrate collection for each user_id and minute
        minute_heart_rate_df = pd.DataFrame(minute_heart_rate_collection.find({'account_id': {
                                    '$in': fitbit_account_id_list}}, {'_id': 0, 'time': 1, 'heart_rate': 1, 'account_id': 1}))

        logging.info("Minute-level heart rates are loaded: {}".format(minute_heart_rate_df.shape[0]))

        # 4.2 merge the minute-level steps with fitbit_api_account_df
        minute_heart_rate_df = pd.merge(
            minute_heart_rate_df, fitbit_api_account_df, on='account_id', how='left')
        minute_heart_rate_df = minute_heart_rate_df[['user_id', 'time', 'heart_rate']]
        minute_heart_rate_df['time'] = pd.to_datetime(
            minute_heart_rate_df['time']).dt.tz_convert('America/Los_Angeles')

        # 4.3 reorganize the minute-level steps to list of integers of each day. insert 0s for missing minutes
        minute_heart_rate_df['date_str'] = minute_heart_rate_df['time'].dt.strftime('%Y-%m-%d')

        user_id_date_str_groupby = minute_heart_rate_df.groupby(['user_id', 'date_str'])
        minute_agg_heart_rate_df = pd.DataFrame(columns=['user_id', 'date_str', 'steps'])

        # iterate through each user_id and date with for and pandas applymap
        @ray.remote
        def process_minute_heart_rate(user_id, date_str, user_id_date_str_df):
            minutes = [0] * 24 * 60

            for i, row in user_id_date_str_df.iterrows():
                minutes[row['time'].hour * 60 + row['time'].minute] = row['heart_rate']

            # make a list for non-zero minutes
            non_zero_minutes = [x for x in minutes if x > 0]

            # calculate the 60,000 times of inverse of the non-zero minutes
            non_zero_minutes_inverse = [60000 / x for x in non_zero_minutes]

            # calculate the standard deviation of the non-zero minutes
            daily_heart_rate_stdev = np.std(non_zero_minutes_inverse)

            return {'user_id': user_id, 'date_str': date_str, 'heart_rates': minutes, 'daily_heart_rate_stdev': daily_heart_rate_stdev, 'non_zero_minutes': len([x for x in minutes if x > 0])}

        object_storage = {}
        logging.info(msg="Pre-loading the data to process minute heart rates for {} users".format(len(user_id_date_str_groupby.groups)))
        for user_id, date_str in user_id_date_str_groupby.groups:
            user_id_date_str_df = user_id_date_str_groupby.get_group((user_id, date_str))
            object_storage["{}_{}".format(user_id, date_str)] = ray.put(user_id_date_str_df)

        logging.info(msg="Constructing the future list of ray tasks")
        minute_agg_heart_rate_list_future = [
            process_minute_heart_rate.remote(user_id, date_str, object_storage["{}_{}".format(user_id, date_str)]) for user_id, date_str in user_id_date_str_groupby.groups
        ]

        logging.info(msg="Waiting for the ray tasks to finish")
        minute_agg_heart_rate_list = ray.get(minute_agg_heart_rate_list_future)
        logging.info(msg="Finished waiting for the ray tasks to finish. Constructing the pd.DataFrame from the list of dicts.")
        minute_agg_heart_rate_df = pd.DataFrame(minute_agg_heart_rate_list)
        logging.info(msg="Finished constructing the pd.DataFrame from the list of dicts.")
        logging.debug(msg="minute_agg_heart_rate_df: \n{}".format(minute_agg_heart_rate_df))

        # 4.4 insert the minute-level steps into the database

        # insert the steps list into the minute_step collection
        logging.info(msg="Inserting the steps list into the minute_step collection")
        minute_heart_rate_collection_t = tdb['minute_heart_rate']
        minute_heart_rate_collection_t.insert_many(minute_agg_heart_rate_df.to_dict('records'))
        logging.info(msg="Finished inserting the steps list into the minute_step collection. rows: {}".format(minute_agg_heart_rate_df.shape[0]))

def copy_daily_steps_and_heart_rate():
    if COLLECTION_DAILY in SETTINGS_REFRESH_COLLECTIONS:
        logging.info(msg="Starting copy_daily_steps_and_heart_rate()")
        # 1. connect to the database
        # create a client instance of the MongoClient class
        tdb = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')
        collection_name = COLLECTION_DAILY
        
        # 2. fetch the current daily collection
        logging.info(msg="Fetching the current daily collection")
        daily_collection = tdb[collection_name]
        daily_df = pd.DataFrame(daily_collection.find({}, {'_id': 0}))
        
        # 3. fetch the current steps collection
        logging.info(msg="Fetching the current steps collection")
        steps_collection = tdb['minute_step']
        steps_df = pd.DataFrame(steps_collection.find({}, {'_id': 0, 'user_id': 1, 'date_str': 1, 'daily_step_sum': 1, 'non_zero_minutes': 1}))

        # 4. rename the columns
        steps_df = steps_df.rename(columns={'daily_step_sum': 'steps', 'non_zero_minutes': 'non_zero_step_minutes'})

        # 5. fetch the current heart rate collection
        logging.info(msg="Fetching the current heart rate collection")
        heart_rate_collection = tdb['minute_heart_rate']
        heart_rate_df = pd.DataFrame(heart_rate_collection.find({}, {'_id': 0, 'user_id': 1, 'date_str': 1, 'daily_heart_rate_stdev': 1, 'non_zero_minutes': 1}))

        # 6. rename the columns
        heart_rate_df = heart_rate_df.rename(columns={'daily_heart_rate_stdev': 'heart_rate_stdev', 'non_zero_minutes': 'wearing_minutes'})
        heart_rate_df['wearing_pct'] = heart_rate_df['wearing_minutes'] / (24 * 60)

        # 7. merge the daily_df with steps_df and heart_rate_df
        logging.info(msg="Merging the daily_df with steps_df")
        logging.info(msg="daily_df.shape: {}".format(daily_df.shape))
        logging.info(msg="steps_df.shape: {}".format(steps_df.shape))
        daily_df = daily_df.merge(steps_df, on=['user_id', 'date_str'], how='left')
        logging.info(msg="Merging the daily_df with heart_rate_df")
        logging.info(msg="daily_df.shape: {}".format(daily_df.shape))
        logging.info(msg="heart_rate_df.shape: {}".format(heart_rate_df.shape))
        daily_df = daily_df.merge(heart_rate_df, on=['user_id', 'date_str'], how='left')
        logging.info(msg="daily_df.shape: {}".format(daily_df.shape))

        # 8. update the daily collection
        logging.info(msg="Updating the daily collection")

        daily_collection.bulk_write([
            UpdateOne(
                {'user_id': row['user_id'], 'date_str': row['date_str']},
                {'$set': {
                    'steps': row['steps'],
                    'non_zero_step_minutes': row['non_zero_step_minutes'],
                    'heart_rate_stdev': row['heart_rate_stdev'],
                    'wearing_minutes': row['wearing_minutes'],
                    'wearing_pct': row['wearing_pct']
                }}
            ) for index, row in daily_df.iterrows()
        ])