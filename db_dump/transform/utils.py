from config import MONGO_DB_URI_DESTINATION
from pymongo import MongoClient
import pandas as pd
import logging
from noaa_sdk import NOAA
import os

def get_database(uri:str, database_name:str):
    client = MongoClient(uri)
    return client[database_name]

def get_participant_list():
    db = get_database(MONGO_DB_URI_DESTINATION, 'justwalk_t')
    participants = db['participants']
    return list(participants.distinct(key='user_id'))

def build_df_from_collection(db, collection_name, filter_dict, projection_dict, rename_columns=None) -> pd.DataFrame:
    """
    Build a pandas DataFrame from a MongoDB collection
    :param db: the database instance
    :param collection_name: the collection name
    :param filter_dict: the filter dictionary
    :param projection_dict: the projection dictionary
    :return: the pandas DataFrame
    """
    collection = db[collection_name]
    df = pd.DataFrame(
        list(collection.find(filter_dict, projection_dict)))
    
    # rename the columns
    if rename_columns is not None:
        df.rename(columns=rename_columns, inplace=True)
    return df

def extend_df_with_collection(df, db, collection_name, filter_dict, projection_dict, on, how='right', rename_columns:list=None) -> pd.DataFrame:
    """
    Extend a pandas DataFrame with a MongoDB collection
    :param df: the pandas DataFrame
    :param db: the database instance
    :param collection_name: the collection name
    :param filter_dict: the filter dictionary
    :param projection_dict: the projection dictionary
    :param on: the join key
    :param how: the join type
    :param rename_columns: the dictionary of columns to rename
    :return: the extended pandas DataFrame
    """
    collection = db[collection_name]
    df2 = pd.DataFrame(
        list(collection.find(filter_dict, projection_dict)))
    
    # rename the columns
    if rename_columns is not None:
        df2.rename(columns=rename_columns, inplace=True)
    
    df = pd.merge(df, df2, on=on, how=how)
    return df

def df_info(df, name, save=False):
    logging.info("{}.shape: {}".format(name, df.shape))
    logging.debug("{}.columns: \n{}".format(name, df.columns))
    logging.debug("{}.dtypes: \n{}".format(name, df.dtypes))
    logging.debug("{}.head(): \n{}".format(name, df.head()))

    if save:
        df.to_csv('{}.csv'.format(name), index=False)
    
def get_weather_observations_df_for_station(station_id: str, start_date: str,
                          end_date: str) -> pd.DataFrame:
    """Get observations for zipcode and convert to dataframe"""

    
    if station_id.startswith('GHCND:'):
        stripped_station_id = station_id[6:]
    else:
        stripped_station_id = station_id

    filename = "db_dump/data/weather/weather_{}.csv".format(stripped_station_id)
    if os.path.exists(filename):
        result_df = pd.read_csv(filename)
        print("result_df.shape: ", result_df.shape)
        return result_df
    else:
        try:
            url = "https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&datatypes=PRCP,AWND,TMAX,TMIN&stations={}&startDate={}&endDate={}&units=metric".format(stripped_station_id, start_date, end_date)
            print("Reading csv from url: ", url)

            result_df = pd.read_csv(
                url
            )
            result_df.to_csv(filename, index=False)
            print("result_df.shape: ", result_df.shape)
            return result_df
        except Exception as e:
            print("Error: ", e)
            return pd.DataFrame()