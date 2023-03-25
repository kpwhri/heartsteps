from tools import get_mongodb_db, JWPresentation, get_uuid4_filename, draw_heatmap, get_intervention_daily_df
import streamlit as st
import pandas as pd
import numpy as np
import os
import pymongo
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import datetime
from pymongo import MongoClient


# output directory
output_dir = 'db_dump/output'

# create output directory if it does not exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

filepath = os.path.join(output_dir, 'JustWalk data visualization ({}).pptx'.format(
    pd.Timestamp.today().strftime('%Y-%m-%d')))

# open a connection to the database
tdb = get_mongodb_db()

# fetch daily dataset
daily = pd.DataFrame(list(tdb['daily'].find()))

# Default Visualization Parameters
cm_name = 'coolwarm'

# 1. draw a heatmap of the levels
level_df = get_intervention_daily_df(daily)
figure_levels = draw_heatmap(level_df, 
                            index='user_id', 
                            columns='day_index', 
                            values='level_int', 
                            legend_labels=[
                                'Random (RA)', 
                                'N+R (NR)', 
                                'N+O (NO)', 
                                'Full (FU)'
                                ], 
                            xlabel='Day Index', 
                            ylabel='User ID', 
                            legend_title='Values', 
                            figure_name='levels.png', 
                            output_dir=output_dir)

# 2. draw a heatmap of the goals
goals_df = get_intervention_daily_df(daily)
figure_goals = draw_heatmap(goals_df,
                            index='user_id',
                            columns='day_index',
                            values='step_goal',
                            legend_labels=None,
                            xlabel='Day Index',
                            ylabel='User ID',
                            legend_title='Step Goals',
                            figure_name='goals.png',
                            output_dir=output_dir)


jwp = JWPresentation()

# add a table of contents
jwp.toc = {
    'type': 'section',
    'title': 'Table of Contents',
    'items': [
        {
            'type': 'section',
            'title': 'Intervention Components',
            'items': [
                {
                    'type': 'slide',
                    'title': 'Levels',
                    'figure': figure_levels
                },
                {
                    'type': 'slide',
                    'title': 'Goals',
                    'figure': figure_goals
                },
                {
                    'type': 'slide',
                    'title': 'Notifications',
                    'items': []
                }
            ]
        },
        {
            'type': 'section',
            'title': 'Behavioral Measurements',
            'items': [
                {
                    'type': 'slide',
                    'title': 'Steps',
                    'items': []
                },
                {
                    'type': 'slide',
                    'title': 'Heart Rates',
                    'items': []
                },
                {
                    'type': 'slide',
                    'title': 'Activities',
                    'items': []
                }
            ]
        }
    ]
}

jwp.build()
jwp.save(filepath)
jwp.open()
