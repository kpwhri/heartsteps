import datetime
import configparser
import pymongo
import psycopg2
import urllib
import pandas as pd
from pymongo import UpdateOne

def get_config_obj():
    config = configparser.ConfigParser()
    config.read('justwalk_secrets/db_dump_config.ini')
    
    return config

def get_mongodb_client():
    config = get_config_obj()
    mongodb_config = config['MongoDB']
    mongodb_uri = "mongodb://{}:{}@{}:{}/{}".format(mongodb_config['username'], urllib.parse.quote(mongodb_config['password']), mongodb_config['host'], mongodb_config['port'], mongodb_config['db'])
    client = pymongo.MongoClient(mongodb_uri)
    return client

def get_mongodb_db(dbname='justwalk'):
    client = get_mongodb_client()
    db = client[dbname]
    return db

def get_mongodb_collection(collection_name):
    db = get_mongodb_db()
    collection = db[collection_name]
    return collection

def get_postgres_connection():
    """
    Get a connection to PostgreSQL
    """
    config = get_config_obj()
    postgres_config = config['PostgreSQL']
    conn = psycopg2.connect(
        host=postgres_config['host'],
        port=postgres_config['port'],
        database=postgres_config['db'],
        user=postgres_config['username'],
        password=postgres_config['password']
    )
    return conn

def dump_table(table_name, columns, where_clause=None) -> pd.DataFrame:
    """
    Dump a table from PostgreSQL to a pandas DataFrame
    """
    with get_postgres_connection() as conn:
        with conn.cursor() as cur:
            if where_clause is not None:
                cur.execute("SELECT {} FROM {} WHERE {}".format(','.join(columns), table_name, where_clause))
            else:
                cur.execute("SELECT {} FROM {}".format(','.join(columns), table_name))
            rows = cur.fetchall()
            df = pd.DataFrame(rows, columns=columns)
    return df

def dump_to_collection(df, collection_name, key_field='id'):
    """
    Dump a pandas DataFrame to a MongoDB collection
    """
    collection = get_mongodb_collection(collection_name)

    if df.shape[0] > 0:
        for index, column in enumerate(df.columns):
            if df[column].dtype == 'datetime64[ns]':
                df[column] = df[column].astype('str')
            elif isinstance(df[column][0], datetime.date):
                df[column] = df[column].astype('str')
            elif isinstance(df[column][0], datetime.datetime):
                df[column] = df[column].astype('str')

        if isinstance(key_field, str):
            return collection.bulk_write([
                UpdateOne(
                    {key_field: row[key_field]},
                    {'$set': row.to_dict()},
                    upsert=True
                ) for _, row in df.iterrows()])
        elif isinstance(key_field, list):
            bulk_write_buffer = []
            for _, row in df.iterrows():
                filter_dict = {}
                for key in key_field:
                    filter_dict[key] = row[key]

                bulk_write_buffer.append(
                    UpdateOne(
                        filter_dict,
                        {'$set': row.to_dict()},
                        upsert=True
                    )
                )
            if len(bulk_write_buffer) > 0:
                return collection.bulk_write(bulk_write_buffer)
            else:
                return None
        else:
            raise ValueError('key_field must be a string or a list of strings')
    else:
        return None

def drop_all_collections(db):
    """
    Drop all collections in the database
    :param db: the database instance
    """
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)

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
