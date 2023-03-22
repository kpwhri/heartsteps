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

def get_mongodb_db():
    client = get_mongodb_client()
    db = client['justwalk']
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