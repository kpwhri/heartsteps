from config import SETTINGS_REFRESH_COLLECTIONS, MONGO_DB_URI_SOURCE, MONGO_DB_URI_DESTINATION
from utils import get_database, build_df_from_collection, extend_df_with_collection, get_participant_list, df_info
from constants import *
from tqdm import tqdm
import os
import pytz
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

def transform_survey():
    if COLLECTION_SURVEY in SETTINGS_REFRESH_COLLECTIONS:
        logging.info(msg="Starting transform_survey()")
        # 1. connect to the database
        # create a client instance of the MongoClient class
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')

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
        

        # 8. reorder the columns
        logging.info(msg="Reordering the columns")
        survey_df = survey_df[[
            'user_id', 'when_asked', 'when_asked_date_str', 'when_asked_time_str', 
            'question_name', 'question_text', 'question_order',
            'answer_text', 'answer_value', 'answer_order', 'kind', 
            'survey_id', 'surveyquestion_id', 'surveyanswer_id', 'surveyresponse_id']]
        
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
        tdb = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')
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
        tdb = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')
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
        tdb = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')
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
                update={'$set': row.to_dict()},
                upsert=True
            ) for _, row in daily_ema_df.iterrows()
        ])

        logging.info(msg="Finished copy_daily_ema()")

def transform_bout_planning_ema_decision():
    if COLLECTION_SURVEY_BOUT_PLANNING_EMA in SETTINGS_REFRESH_COLLECTIONS:
        logging.info(msg="Starting transform_bout_planning_ema_decision()")
        # 1. connect to the database
        db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
        tdb = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')

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
        bpn_decision_df['when_created_local_dt'] = pd.to_datetime(bpn_decision_df['when_created_local_str'])
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

        # # 2.21. remove errorneous decisions
        # # 2.21.0. define the function to find erroneous decisions
        # @ray.remote
        # def find_erroneous_decisions(group):
        #     pass

        # # 2.21.1. join the BPN decision data with the BPN survey data
        # survey_id_list = bpn_survey_df['survey_id'].tolist()
        
        # # 2.21.1. traverse groups of user_id, date_str, hour_of_day
        # user_id_date_hour_groups = bpn_decision_df.groupby(['user_id', 'date_str', 'hour_of_day'])  # group by user_id, date_str, hour_of_day
        # future_list = []    # prepare the ray futures list

        # # define the function to find erroneous decisions
            
            
        #     # get the number of decisions in the group
        #     num_decisions = group['num_decisions'].iloc[0]
        #     # get the decision_id list
        #     decision_id_list = group['decision_id'].tolist()
        #     # get the erroneous decisions
        #     erroneous_decisions = decision_id_list[num_decisions:]
        #     return erroneous_decisions

        # # 2.21.2. for each group, find the erroneous decisions
        # for name, group in user_id_date_hour_groups:
        #     # if the number of decisions in the group is 1, skip the group
        #     if group.shape[0] == 1:
        #         continue
        #     else:
        #         future_list.append(find_erroneous_decisions.remote(group))
        
        # # 2.21.3. get the list of erroneous decisions
        # erroneous_decisions_list = ray.get(future_list)

        # # 2.21.4. flatten the list of erroneous decisions
        # erroneous_decisions_list = [item for sublist in erroneous_decisions_list for item in sublist]

        # # 2.21.5. remove the erroneous decisions
        # bpn_decision_df = bpn_decision_df[~bpn_decision_df['decision_id'].isin(erroneous_decisions_list)]
        # df_info(bpn_decision_df, name='bpn_decision_df', save=True)

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
        tdb = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')
        collection_name = COLLECTION_SURVEY_BOUT_PLANNING_EMA
        
        # 2. Fetching the current COLLECTION_SURVEY_BOUT_PLANNING_EMA survey documents from COLLECTION_SURVEY
        logging.info(msg="Fetching the current COLLECTION_SURVEY_BOUT_PLANNING_EMA survey documents from COLLECTION_SURVEY")
        
        # 2.1. Get the participant id list
        participant_list = get_participant_list()
        
        # 2.2. Get the survey documents
        # BPN = Bout Planning Survey
        survey_collection = tdb[COLLECTION_SURVEY]
        bpn_df = pd.DataFrame(survey_collection.find({
            'question_name': 'Bout Planning Survey',
            'user_id': {'$in': participant_list}
        }, {'_id': 0}))

        logging.info("survey_df.shape: {}".format(bpn_df.shape))
        logging.debug("survey_df.columns: {}".format(bpn_df.columns))
        logging.debug("survey_df.head(): \n{}".format(bpn_df.head()))

        

def fill_daily_nans():
    if COLLECTION_DAILY in SETTINGS_REFRESH_COLLECTIONS:
        logging.info(msg="Starting fill_daily_nans()")
        # 1. connect to the database
        # create a client instance of the MongoClient class
        tdb = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')
        collection_name = COLLECTION_DAILY
        
        # 2. fetch the current daily collection
        logging.info(msg="Fetching the current daily collection")
        daily_collection = tdb[collection_name]
        daily_df = pd.DataFrame(daily_collection.find({}, {'_id': 0}))
        
        # 3. fill with zeros if there's NaN in the following columns: non_zero_step_minutes, wearing_minutes, wearing_pct, steps, level_int
        logging.info(msg="Filling with zeros if there's NaN in the following columns: non_zero_step_minutes, wearing_minutes, wearing_pct, steps, level_int")
        daily_df['non_zero_step_minutes'] = daily_df['non_zero_step_minutes'].fillna(0)
        daily_df['wearing_minutes'] = daily_df['wearing_minutes'].fillna(0)
        daily_df['wearing_pct'] = daily_df['wearing_pct'].fillna(0)
        daily_df['steps'] = daily_df['steps'].fillna(0)
        daily_df['level_int'] = daily_df['level_int'].fillna(0)
        
        # 4. fill with "RE" if there's NaN in the following columns: level_str
        logging.info(msg="Filling with 'RE' if there's NaN in the following columns: level_str")
        daily_df['level_str'] = daily_df['level_str'].fillna('RE')
        
        # 5. update the daily collection
        logging.info(msg="Updating the daily collection")
        daily_collection.bulk_write([
            UpdateOne(
                {'user_id': row['user_id'], 'date_str': row['date_str']},
                {'$set': {
                    'non_zero_step_minutes': row['non_zero_step_minutes'],
                    'wearing_minutes': row['wearing_minutes'],
                    'wearing_pct': row['wearing_pct'],
                    'steps': row['steps']
                }}
            ) for index, row in daily_df.iterrows()
        ])
