import streamlit as st
import pandas as pd
import numpy as np
import os
import pymongo

from pymongo import MongoClient

## This program is used to transform the data from the database dump (justwalk database, 'db') into a format that is more suitable for the data analysis (transformed database, 'tdb')

version = '0.1.0'

# Path: db_dump/transform.py
pymongo_uri = 'mongodb://root:example@localhost:27017'

# create a client instance of the MongoClient class
client = MongoClient(pymongo_uri)

# create a database instance
db = client['justwalk']
tdb = client['transformed']

# insert a meta data
meta = tdb['meta']

# put the dump path and the date into the meta collection
meta.insert_one({'action': 'transform', 'date': pd.Timestamp.today(), 'when': pd.Timestamp.now(), 'version': version})

