import os, sys, code
#EXPORT_DIR    = os.environ["EXPORT_DIR"] 
#HS_SERVER_DIR = os.environ["HS_SERVER_DIR"] 

import utils
import pandas as pd
import progressbar
import pytz
import numpy as np
import traceback
import argparse

import weekly, daily, within_day, minute, bursts

debug_users =["244"]

def export_all_data(export_dir, cohort="U01", exports=[],DEBUG=True):
    
    print("Starting data export V4")
    
    users = utils.get_users()
    
    count=DEBUG
    for u in users:


        try:
            if(users[u]["cohort"]!=cohort): continue
            if(DEBUG and users[u]["hsid"] not in debug_users): continue

            print("\nExporting data for user: " + u)

            #Setup output directory
            user_export_directory = os.path.join(EXPORT_DIR, users[u]["cohort"], u)
            utils.setup_export_directory(user_export_directory)
        
            #Daily
            if "daily.planning" in exports or "daily.all" in exports: 
                print("\n  Exporting daily planning")
                daily.export_daily_planning_data(users[u], directory = user_export_directory, from_scratch=True)
            
            if "daily.survey" in exports or "daily.all" in exports: 
                print("\n  Exporting morning survey")
                daily.export_daily_morning_survey(users[u], directory = user_export_directory)
            
            if "daily.messages" in exports or "daily.all" in exports:
                print("\n  Exporting morning message")
                daily.export_daily_morning_message(users[u], directory = user_export_directory, from_scratch=True)

            #Weekly
            if("weekly" in exports):
                print("\n  Exporting weekly data")
                weekly.export_weekly_data(users[u], directory = user_export_directory, from_scratch=True)
    
            #Within day
            if "within_day.walking" in exports or "within_day.all" in exports:
                print("\n  Exporting walking suggestions")
                within_day.walking_suggestions(users[u], directory = user_export_directory, from_scratch=True)
            
            if "within_day.antisedintary" in exports or "within_day.all" in exports:
                print("\n  Exporting antisedentary suggestions")
                within_day.antisedintary_suggestions(users[u], directory = user_export_directory, from_scratch=True)

            #Minute
            if "minute.fitbit" in exports or "minute.all" in exports:
                print("\n  Exporting minute level fitbit")
                minute.export_fitbit_minute_data(users[u], directory = user_export_directory)

            #Burst
            if "burst.walking" in exports or "burst.all" in exports:
                print("\n  Exporting burst walking survey")
                bursts.export_burst_walking_survey(users[u], directory = user_export_directory)
            
            if "burst.activity" in exports or "burst.all" in exports:
                print("\n  Exporting burst activity survey")
                bursts.export_burst_activity_survey(users[u], directory = user_export_directory)
        
        except Exception as e:
            print("Error exporting data for user: " + u)
            print(e)
            traceback.print_exc()


if __name__ == "__main__":

    config = utils.read_config()
    EXPORT_DIR = config["EXPORT_DIR"]

    parser = argparse.ArgumentParser(description='Run data export.')
    parser.add_argument('-d',help='use debug mode',dest='debug', action='store_const', const=True, default=False)

    parser.add_argument('levels', metavar='l', nargs='+',
                        help='list of export levels (e.g., weekly, daily, minute)')

    args = parser.parse_args()        

    print("Exporting levels: ", ", ".join(args.levels)," with DEBUG=",str(args.debug))

    export_all_data(EXPORT_DIR, cohort='U01',exports=args.levels,DEBUG=args.debug)