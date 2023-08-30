from config import SETTINGS_OUTPUT_DIR, SETTINGS_OUTPUT_FILENAME, MONGO_DB_URI_DESTINATION, MONGO_DB_URI_SOURCE
from utils import get_database, get_intervention_daily_df, draw_heatmap, draw_distribution_heatmap, JWPresentation, JWSection, draw_sorted_bars, draw_scatterplot
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Patch
from pptx import Presentation
import logging

def do_one_time(param):
    # get the database
    db = get_database(MONGO_DB_URI_SOURCE, 'justwalk')
    fb_update_collection = db['fitbit_api_fitbitaccountupdate']
    
    list_of_fb_accounts = fb_update_collection.distinct('account_id')
    
    for fb_account_id in list_of_fb_accounts:
        fb_update_df = pd.DataFrame(list(fb_update_collection.find({'account_id': fb_account_id})))
        print("fb_account_id: {}, fb_update_df.shape: {}".format(fb_account_id, fb_update_df.shape))

        # convert the created column to datetime
        fb_update_df['created'] = pd.to_datetime(fb_update_df['created']).dt.tz_convert('America/Los_Angeles')

        # create a new column for the hour timepoint. for example, 2019-01-01 00:01:23 will be 2019-01-01 00:00:00
        fb_update_df['created_hour'] = fb_update_df['created'].dt.floor('h', ambiguous='NaT')

        # filter all rows with NaT in created_hour
        fb_update_df = fb_update_df[fb_update_df['created_hour'].notnull()]

        # group by created_hour and count the number of rows
        fb_update_df_summary = fb_update_df.groupby('created_hour').count().reset_index()

        # filter out the rows with counts higher than 5
        fb_update_df_summary = fb_update_df_summary[fb_update_df_summary['created'] <= 5]

        # fill the missing hours with 0
        fb_update_df_summary = fb_update_df_summary.set_index('created_hour').resample('H').sum().fillna(0).reset_index()

        # rename the columns
        fb_update_df_summary = fb_update_df_summary.rename(columns={'created': 'count'})

        # create a new column for the day
        fb_update_df_summary['day'] = fb_update_df_summary['created_hour'].dt.floor('d', ambiguous='NaT')

        # create a new column for the hour
        fb_update_df_summary['hour'] = fb_update_df_summary['created_hour'].dt.hour
        
        # draw the heatmap. each row of the heatmap is a day, and each column is an hour.
        output_dir = os.path.join(os.getcwd(), SETTINGS_OUTPUT_DIR)
        draw_heatmap(df=fb_update_df_summary, index='day', columns='hour', values='count', legend_labels=None, xlabel='Hour', ylabel='Day', legend_title='Number of Fitbit Account Updates', figure_name='Number of Fitbit Account Updates by Hour', output_dir=output_dir)

        ######

        # count the number of heart rate data points per hour
        hr_df = pd.DataFrame(list(db['fitbit_activities_fitbitminuteheartrate'].find({'account_id': fb_account_id})))

        # filter out the rows with 0 heart rate
        hr_df = hr_df[hr_df['heart_rate'] > 0]

        hr_df['created'] = pd.to_datetime(hr_df['time']).dt.tz_convert('America/Los_Angeles')
        hr_df['created_hour'] = hr_df['created'].dt.floor('h', ambiguous='NaT')
        hr_df = hr_df[hr_df['created_hour'].notnull()]
        hr_df_summary = hr_df.groupby('created_hour').count().reset_index()
        hr_df_summary = hr_df_summary.set_index('created_hour').resample('H').sum().fillna(0).reset_index()
        hr_df_summary = hr_df_summary.rename(columns={'created': 'count'})
        hr_df_summary['day'] = hr_df_summary['created_hour'].dt.floor('d', ambiguous='NaT')
        hr_df_summary['hour'] = hr_df_summary['created_hour'].dt.hour

        # remove the extreme outliers. the maximum number of heart rate data points per hour is 60 
        hr_df_summary = hr_df_summary[hr_df_summary['count'] <= 60]

        # draw the heatmap. each row of the heatmap is a day, and each column is an hour.
        draw_heatmap(df=hr_df_summary, index='day', columns='hour', values='count', legend_labels=None, xlabel='Hour', ylabel='Day', legend_title='Number of Heart Rate Data Points', figure_name='Number of Heart Rate Data Points by Hour', output_dir=output_dir)

        
        ######

        # to draw a scatter plot of the number of heart rate data points vs. the number of fitbit account updates, create a new dataframe
        hr_fb_df = pd.merge(fb_update_df_summary, hr_df_summary, on=['day', 'hour'], how='inner').copy()

        # rename the columns
        hr_fb_df = hr_fb_df.rename(columns={'count_x': 'count_fb', 'count_y': 'count_hr'})

        # draw the scatter plot
        draw_scatterplot(
            df=hr_fb_df,
            x='count_fb',
            y='count_hr',
            regline=False,
            x_jitter=0.3,
            y_jitter=1,
            size=0.5,
            xlabel='Number of Fitbit Account Updates',
            ylabel='Number of Heart Rate Data Points',
            figure_name='Number of Heart Rate Data Points vs Number of Fitbit Account Updates',
            output_dir=output_dir
        )




if __name__ == '__main__':
    param = {}
    do_one_time(param)