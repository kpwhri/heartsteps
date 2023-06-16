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

import weekly, daily, within_day, minute, bursts, logs

debug_users =["244"]

def export_all_data(EXPORT_DIR, cohort="U01", exports=[],DEBUG=True):
    
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
            if "daily.fitbitactivity" in exports or "daily" in exports or "all" in exports:
                print("\n  Exporting daily fitbit activity")
                daily.export_daily_fitbit_activity_data(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

            if "daily.planning" in exports or "daily" in exports or "all" in exports:
                print("\n  Exporting daily planning")
                daily.export_daily_planning_data(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

            if "daily.appuse" in exports or "daily" in exports or "all" in exports:
                print("\n  Exporting daily app use")
                daily.export_daily_app_use_data(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

            if "daily.notifications" in exports or "daily" in exports or "all" in exports:
                print("\n  Exporting daily notifications")
                daily.export_daily_notification_data(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

            if "daily.survey" in exports or "daily" in exports  or "all" in exports:
                print("\n  Exporting morning survey")
                daily.export_daily_morning_survey(users[u], directory = user_export_directory,DEBUG=DEBUG)
            
            if "daily.messages" in exports or "daily" in exports  or "all" in exports:
                print("\n  Exporting morning message")
                daily.export_daily_morning_message(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

            if "daily.walkingsuggestions" in exports or "daily" in exports  or "all" in exports:
                print("\n  Exporting daily walking suggestions")
                daily.export_daily_walking_suggestions(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

            if "daily.antidesentarysuggestions" in exports or "daily" in exports  or "all" in exports:
                print("\n  Exporting daily antidesentary suggestions")
                daily.export_daily_antidesentary_suggestions(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

            if "daily.fitbit" in exports or "daily" in exports  or "all" in exports:
                print("\n  Exporting daily fitbit data")
                daily.export_daily_fitbit_data(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)


            #Weekly
            if "weekly.planning" in exports or "weekly" in exports or "all" in exports:
                print("\n  Exporting weekly planning data")
                weekly.export_weekly_planning(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)
    
            if "weekly.survey" in exports or "weekly" in exports or "all" in exports:
                print("\n  Exporting weekly survey")
                weekly.export_weekly_survey(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

            if "weekly.fitbitactivity" in exports or "weekly" in exports or "all" in exports:
                print("\n  Exporting weekly fitbit activity")
                weekly.export_weekly_fitbit_activity_data(users[u], directory=user_export_directory, from_scratch=True, DEBUG=DEBUG)

            if "weekly.appuse" in exports or "weekly" in exports or "all" in exports:
                print("\n  Exporting weekly app use")
                weekly.export_weekly_app_use_data(users[u], directory=user_export_directory, from_scratch=True, DEBUG=DEBUG)

            if "weekly.notifications" in exports or "weekly" in exports or "all" in exports:
                print("\n  Exporting weekly notifications")
                weekly.export_weekly_notification_data(users[u], directory=user_export_directory, from_scratch=True, DEBUG=DEBUG)

            if "weekly.walkingsuggestions" in exports or "weekly" in exports or "all" in exports:
                print("\n  Exporting weekly walking suggestions")
                weekly.export_weekly_walking_suggestions(users[u], directory=user_export_directory, from_scratch=True, DEBUG=DEBUG)

            if "weekly.antidesentarysuggestions" in exports or "weekly" in exports or "all" in exports:
                print("\n  Exporting weekly antidesentary suggestions")
                weekly.export_weekly_antidesentary_suggestions(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

            if "weekly.fitbit" in exports or "weekly" in exports or "all" in exports:
                print("\n  Exporting weekly fitbit data")
                weekly.export_weekly_fitbit_data(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

            #Within day
            if "withinday.walking" in exports or "withinday" in exports or "all" in exports:
                print("\n  Exporting walking suggestions")
                within_day.walking_suggestions(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)
            
            if "withinday.antisedintary" in exports or "withinday" in exports or "all" in exports:
                print("\n  Exporting antisedentary suggestions")
                within_day.antisedentary_suggestions(users[u], directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

            #Minute
            if "minute.fitbit" in exports or "minute" in exports or "all" in exports:
                print("\n  Exporting minute level fitbit")
                minute.export_fitbit_minute_data(users[u], directory = user_export_directory,DEBUG=DEBUG)

            #Burst
            if "burst.walking" in exports or "burst" in exports or "all" in exports:
                print("\n  Exporting burst walking survey")
                bursts.export_burst_walking_survey(users[u], directory = user_export_directory,DEBUG=DEBUG)
            
            if "burst.activity" in exports or "burst" in exports or "all" in exports:
                print("\n  Exporting burst activity survey")
                bursts.export_burst_activity_survey(users[u], directory = user_export_directory,DEBUG=DEBUG)
        
            #Log
            if "logs.fitbit" in exports or "logs" in exports or "all" in exports:
                print("\n  Exporting fitbit activity log")
                logs.export_fitbit_activity_log(users[u], directory = user_export_directory,DEBUG=DEBUG)
            
            if "logs.notifications" in exports or "logs" in exports or "all" in exports:
                print("\n  Exporting notification log")
                logs.export_notification_log(users[u], directory = user_export_directory,DEBUG=DEBUG)

            if "logs.appuse" in exports or "logs" in exports or "all" in exports:
                print("\n  Exporting pageview log")
                logs.export_app_use_log(users[u], directory = user_export_directory,DEBUG=DEBUG)

            if "logs.planning" in exports or "logs" in exports or "all" in exports:
                print("\n  Exporting planning log")
                logs.export_planning_log(users[u], directory = user_export_directory,DEBUG=DEBUG)

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