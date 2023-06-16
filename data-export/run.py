import os, sys, code
from multiprocessing.pool import ThreadPool
import utils
import pandas as pd
import progressbar
import pytz
import numpy as np
import traceback
import argparse

import weekly, daily, within_day, minute, bursts, logs

debug_users =["244"]

def export_all_data(EXPORT_DIR, cohort="U01", exports=[],DEBUG=True,user_filter=None,threaded=True):
    
    print("Starting data export V4")
    
    users = utils.get_users()

    if threaded:
        pool = ThreadPool(8)
        f = lambda u: export_data(u,EXPORT_DIR, cohort, exports,DEBUG)
        pool.imap(f,users.values())

    else: 
        for u in users:
            if user_filter is not None and users[u]["hsid"] not in user_filter: continue
            if(users[u]["cohort"]!=cohort): continue
            if(DEBUG and users[u]["hsid"] not in debug_users): continue
            export_data(users[u],EXPORT_DIR, cohort, exports,DEBUG)

def export_data(user,EXPORT_DIR, cohort="U01", exports=[],DEBUG=True):

    try:
        
        u = user["hsid"]
        print("\nExporting data for user: " + u)

        #Setup output directory
        user_export_directory = os.path.join(EXPORT_DIR, user["cohort"], u)
        utils.setup_export_directory(user_export_directory)
    
        #Daily
        if "daily.fitbitactivity" in exports or "daily" in exports or "all" in exports:
            print(f"\n   {u}: Exporting daily fitbit activity")
            daily.export_daily_fitbit_activity_data(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

        if "daily.planning" in exports or "daily" in exports or "all" in exports:
            print(f"\n   {u}: Exporting daily planning")
            daily.export_daily_planning_data(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

        if "daily.appuse" in exports or "daily" in exports or "all" in exports:
            print(f"\n   {u}: Exporting daily app use")
            daily.export_daily_app_use_data(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

        if "daily.notifications" in exports or "daily" in exports or "all" in exports:
            print(f"\n   {u}: Exporting daily notifications")
            daily.export_daily_notification_data(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

        if "daily.survey" in exports or "daily" in exports  or "all" in exports:
            print(f"\n   {u}: Exporting morning survey")
            daily.export_daily_morning_survey(user, directory = user_export_directory,DEBUG=DEBUG)
        
        if "daily.messages" in exports or "daily" in exports  or "all" in exports:
            print(f"\n   {u}: Exporting morning message")
            daily.export_daily_morning_message(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

        if "daily.walkingsuggestions" in exports or "daily" in exports  or "all" in exports:
            print(f"\n   {u}: Exporting daily walking suggestions")
            daily.export_daily_walking_suggestions(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

        if "daily.antidesentarysuggestions" in exports or "daily" in exports  or "all" in exports:
            print(f"\n   {u}: Exporting daily antidesentary suggestions")
            daily.export_daily_antidesentary_suggestions(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

        if "daily.fitbit" in exports or "daily" in exports  or "all" in exports:
            print(f"\n   {u}: Exporting daily fitbit data")
            daily.export_daily_fitbit_data(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)


        #Weekly
        if "weekly.planning" in exports or "weekly" in exports or "all" in exports:
            print(f"\n   {u}: Exporting weekly planning data")
            weekly.export_weekly_planning(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

        if "weekly.survey" in exports or "weekly" in exports or "all" in exports:
            print(f"\n   {u}: Exporting weekly survey")
            weekly.export_weekly_survey(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

        if "weekly.fitbitactivity" in exports or "weekly" in exports or "all" in exports:
            print(f"\n   {u}: Exporting weekly fitbit activity")
            weekly.export_weekly_fitbit_activity_data(user, directory=user_export_directory, from_scratch=True, DEBUG=DEBUG)

        if "weekly.appuse" in exports or "weekly" in exports or "all" in exports:
            print(f"\n   {u}: Exporting weekly app use")
            weekly.export_weekly_app_use_data(user, directory=user_export_directory, from_scratch=True, DEBUG=DEBUG)

        if "weekly.notifications" in exports or "weekly" in exports or "all" in exports:
            print(f"\n   {u}: Exporting weekly notifications")
            weekly.export_weekly_notification_data(user, directory=user_export_directory, from_scratch=True, DEBUG=DEBUG)

        if "weekly.walkingsuggestions" in exports or "weekly" in exports or "all" in exports:
            print(f"\n   {u}: Exporting weekly walking suggestions")
            weekly.export_weekly_walking_suggestions(user, directory=user_export_directory, from_scratch=True, DEBUG=DEBUG)

        if "weekly.antidesentarysuggestions" in exports or "weekly" in exports or "all" in exports:
            print(f"\n   {u}: Exporting weekly antidesentary suggestions")
            weekly.export_weekly_antidesentary_suggestions(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

        if "weekly.fitbit" in exports or "weekly" in exports or "all" in exports:
            print(f"\n   {u}: Exporting weekly fitbit data")
            weekly.export_weekly_fitbit_data(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

        #Within day
        if "withinday.walking" in exports or "withinday" in exports or "all" in exports:
            print(f"\n   {u}: Exporting walking suggestions")
            within_day.walking_suggestions(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)
        
        if "withinday.antisedintary" in exports or "withinday" in exports or "all" in exports:
            print(f"\n   {u}: Exporting antisedentary suggestions")
            within_day.antisedentary_suggestions(user, directory = user_export_directory, from_scratch=True,DEBUG=DEBUG)

        #Minute
        if "minute.fitbit" in exports or "minute" in exports or "all" in exports:
            print(f"\n   {u}: Exporting minute level fitbit")
            minute.export_fitbit_minute_data(user, directory = user_export_directory,DEBUG=DEBUG)

        #Burst
        if "burst.walking" in exports or "burst" in exports or "all" in exports:
            print(f"\n   {u}: Exporting burst walking survey")
            bursts.export_burst_walking_survey(user, directory = user_export_directory,DEBUG=DEBUG)
        
        if "burst.activity" in exports or "burst" in exports or "all" in exports:
            print(f"\n   {u}: Exporting burst activity survey")
            bursts.export_burst_activity_survey(user, directory = user_export_directory,DEBUG=DEBUG)
    
        #Log
        if "logs.fitbit" in exports or "logs" in exports or "all" in exports:
            print(f"\n   {u}: Exporting fitbit activity log")
            logs.export_fitbit_activity_log(user, directory = user_export_directory,DEBUG=DEBUG)
        
        if "logs.notifications" in exports or "logs" in exports or "all" in exports:
            print(f"\n   {u}: Exporting notification log")
            logs.export_notification_log(user, directory = user_export_directory,DEBUG=DEBUG)

        if "logs.appuse" in exports or "logs" in exports or "all" in exports:
            print(f"\n   {u}: Exporting pageview log")
            logs.export_app_use_log(user, directory = user_export_directory,DEBUG=DEBUG)

        if "logs.planning" in exports or "logs" in exports or "all" in exports:
            print(f"\n   {u}: Exporting planning log")
            logs.export_planning_log(user, directory = user_export_directory,DEBUG=DEBUG)

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