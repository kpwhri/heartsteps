import os, sys, code
EXPORT_DIR    = os.environ["EXPORT_DIR"] 
HS_SERVER_DIR = os.environ["HS_SERVER_DIR"] 
DEBUG         = False

import utils
import pandas as pd
import progressbar
import pytz
import numpy as np

import weekly_planning

utils.setup()

def export_all_data(export_dir, cohort="U01"):
    
    print("Starting data export V4")
    
    users = utils.get_users()
    
    count=0
    for u in users:
        #try:
        if(users[u]["cohort"]!=cohort): continue

        print("Exporting data for user: " + u)

        #Setup output directory
        user_export_directory = os.path.join(EXPORT_DIR, users[u]["cohort"], u)
        utils.setup_export_directory(user_export_directory)
    
        #Run exports
        weekly_planning.export_weekly_data(users[u], directory = user_export_directory, from_scratch=True)
        
        #except Exception as e:
        #    print("Error exporting data for user: " + u)
        #    print(e)

        if(DEBUG==True and count>=2):
            break        
        count=count+1

if __name__ == "__main__":
    export_all_data(EXPORT_DIR, cohort='U01')