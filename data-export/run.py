import os, sys, code
EXPORT_DIR    = os.environ["EXPORT_DIR"] 
HS_SERVER_DIR = os.environ["HS_SERVER_DIR"] 

import utils
import pandas as pd
import progressbar
import pytz
import numpy as np
import traceback
import argparse

import weekly, daily, minute

def export_all_data(export_dir, cohort="U01", exports=[],DEBUG=True):
    
    print("Starting data export V4")
    
    users = utils.get_users()
    
    count=0
    for u in users:
        try:
            if(users[u]["cohort"]!=cohort): continue

            print("Exporting data for user: " + u)

            #Setup output directory
            user_export_directory = os.path.join(EXPORT_DIR, users[u]["cohort"], u)
            utils.setup_export_directory(user_export_directory)
        
            #Run exports
            if("daily" in exports):
                daily.export_daily_planning_data(users[u], directory = user_export_directory, from_scratch=True)
            
            if("weekly" in exports):
                weekly.export_weekly_data(users[u], directory = user_export_directory, from_scratch=True)
    
            if("daily" in exports):
                minute.export_fitbit_minute_data(users[u], directory = user_export_directory)
            
        except Exception as e:
            print("Error exporting data for user: " + u)
            print(e)
            traceback.print_exc()

        if(DEBUG==True and count>=1):
            break        
        count=count+1

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Run data export.')
    parser.add_argument('-d',help='use debug mode',dest='debug', action='append_const', const=True, default=False)

    parser.add_argument('levels', metavar='l', nargs='+',
                        help='list of export levels (e.g., weekly, daily, minute)')

    args = parser.parse_args()        

    print("Exporting levels: ", ", ".join(args.levels)," with DEBUG=",str(args.debug))

    export_all_data(EXPORT_DIR, cohort='U01',exports=args.levels,DEBUG=args.debug)