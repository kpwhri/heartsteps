from config import SETTINGS_OUTPUT_DIR, SETTINGS_OUTPUT_FILENAME, MONGO_DB_URI_DESTINATION
from utils import get_database, get_intervention_daily_df, draw_heatmap, JWPresentation
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Patch
from pptx import Presentation

def prepare():
    # create output directory if it does not exist
    output_dir = os.path.join(os.getcwd(), SETTINGS_OUTPUT_DIR)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

def form_the_presentation(filename_dict):
    output_dir = os.path.join(os.getcwd(), SETTINGS_OUTPUT_DIR)
    filepath = os.path.join(output_dir, "{} ({}).pptx".format(SETTINGS_OUTPUT_FILENAME, pd.Timestamp.today().strftime('%Y-%m-%d')))

    jwp = JWPresentation()

    # add a table of contents
    jwp.toc = {
        'type': 'section',
        'title': 'Table of Contents',
        'items': [
            {
                'type': 'section',
                'title': 'Daily Data',
                'items': [
                    {
                        'type': 'slide',
                        'title': 'Levels',
                        'figure': filename_dict['levels']
                    },
                    {
                        'type': 'slide',
                        'title': 'Goals',
                        'figure': filename_dict['goals']
                    },
                    {
                        'type': 'slide',
                        'title': 'Steps',
                        'figure': filename_dict['steps'],
                        'note': '* Note: steps are capped at 20,000'
                    },
                    {
                        'type': 'section',
                        'title': 'Heart Rates',
                        'items': [
                            {
                                'type': 'slide',
                                'title': 'Wear Time Percentage',
                                'figure': filename_dict['wearing_time_pct'],
                            },
                            {
                                'type': 'slide',
                                'title': 'Heart Rate Variability',
                                'figure': filename_dict['heart_rates_hrv'],
                                'note': '* Note: heart rate variability is capped at 300'
                            }
                        ]
                    }
                ]
            }
        ]
    }

    jwp.build()
    jwp.save(filepath)
    jwp.open()



def draw_level_heatmap():
    # Default Visualization Parameters
    cm_name = 'coolwarm'
    output_dir = os.path.join(os.getcwd(), SETTINGS_OUTPUT_DIR)

    # get the database
    db = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')
    daily = pd.DataFrame(list(db['daily'].find()))

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

    return figure_levels

def draw_goal_heatmap():
    # Default Visualization Parameters
    cm_name = 'coolwarm'
    output_dir = os.path.join(os.getcwd(), SETTINGS_OUTPUT_DIR)

    # get the database
    db = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')
    daily = pd.DataFrame(list(db['daily'].find()))

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

    return figure_goals

def draw_steps_heatmap():
    # Default Visualization Parameters
    cm_name = 'coolwarm'
    output_dir = os.path.join(os.getcwd(), SETTINGS_OUTPUT_DIR)

    # get the database
    db = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')
    daily = pd.DataFrame(list(db['daily'].find()))

    # 3. draw a heatmap of the steps
    steps_df = get_intervention_daily_df(daily)

    # 4. cut off the steps at 20,000
    steps_df.loc[steps_df['steps'] > 20000, 'steps'] = 20000

    figure_steps = draw_heatmap(steps_df, 
                                index='user_id', 
                                columns='day_index', 
                                values='steps', 
                                legend_labels=None, 
                                xlabel='Day Index', 
                                ylabel='User ID', 
                                legend_title='Steps', 
                                figure_name='steps.png', 
                                output_dir=output_dir)

    return figure_steps

def draw_heart_rate_hrv_heatmap():
    # Default Visualization Parameters
    cm_name = 'coolwarm'
    output_dir = os.path.join(os.getcwd(), SETTINGS_OUTPUT_DIR)

    # get the database
    db = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')
    daily = pd.DataFrame(list(db['daily'].find()))

    # draw a heatmap of the heart rate variability
    hrv_df = get_intervention_daily_df(daily)

    # cap the heart rate variability at 300
    hrv_df.loc[hrv_df['heart_rate_stdev'] > 300, 'heart_rate_stdev'] = 300

    figure_hrv = draw_heatmap(hrv_df, 
                                index='user_id', 
                                columns='day_index', 
                                values='heart_rate_stdev', 
                                legend_labels=None, 
                                xlabel='Day Index', 
                                ylabel='User ID', 
                                legend_title='Heart Rate Variability (HRV)', 
                                figure_name='heart_rates_hrv.png', 
                                output_dir=output_dir)

    return figure_hrv

def draw_wearing_time_pct_heatmap():
    # Default Visualization Parameters
    cm_name = 'coolwarm'
    output_dir = os.path.join(os.getcwd(), SETTINGS_OUTPUT_DIR)

    # get the database
    db = get_database(MONGO_DB_URI_DESTINATION, 'justwalk')
    daily = pd.DataFrame(list(db['daily'].find()))

    # draw a heatmap of the wearing time percentage
    wearing_time_pct_df = get_intervention_daily_df(daily)

    # convert to percentage
    wearing_time_pct_df['wearing_pct'] = wearing_time_pct_df['wearing_pct'] * 100

    figure_wearing_time_pct = draw_heatmap(wearing_time_pct_df, 
                                index='user_id', 
                                columns='day_index', 
                                values='wearing_pct', 
                                legend_labels=None, 
                                xlabel='Day Index', 
                                ylabel='User ID', 
                                legend_title='Wearing Time Percentage', 
                                figure_name='wearing_time_pct.png', 
                                output_dir=output_dir)

    return figure_wearing_time_pct