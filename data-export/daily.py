import pandas as pd
import pytz
import numpy as np
from django.utils import timezone
import os
from datetime import datetime,  date, timedelta, timezone
from math import floor

import utils

from days.models import Day
from days.services import DayService
from contact.models import ContactInformation
from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitMinuteHeartRate
from fitbit_activities.models import FitbitActivity

from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from locations.models import Location
from locations.models import Place

from push_messages.models import Message as PushMessage
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from weekly_reflection.models import ReflectionTime

from participants.services import ParticipantService
from participants.models import Cohort
from participants.models import DataExport
from participants.models import DataExportSummary
from participants.models import DataExportQueue
from participants.models import Study
from participants.models import Participant

from weeks.models import Week
from surveys.models import Survey
from page_views.models import PageView
from activity_plans.models import  ActivityPlan
from activity_logs.models import ActivityLog


def export_daily_planning_data(user,directory = None, filename = None, start=None, end=None, from_scratch=True,DEBUG=True):
    
    dictionary       = pd.read_csv("data_dictionaries/weekly.csv")
    final_field_name = dictionary["ElementName"]
    raw_field_name   = dictionary["Aliases"]
    field_map        = utils.get_field_map(dictionary)
    
    uid = user["uid"]
    username = user["hsid"]
    
    if(DEBUG):
        print("  Exporting daily planning data for: ", username)
    
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.daily_planning.csv'.format(
            username = username
        )
        
    if( (not from_scratch) and os.path.isfile(os.path.join(directory,filename))):
        return
    
    def safe_list_to_str(opts):
        if opts is not None:
            return ",".join(opts)
        else: 
            return np.nan 
    
    #import code
    #code.interact(local=dict(globals(), **locals()))

    #Get all weeks where participant may have been active
    week_query = Week.objects.filter(user=uid).all().values('start_date','end_date')
    start_date = min([week["start_date"] for week in week_query])
    end_date = max([week["end_date"] for week in week_query])
    delta = end_date - start_date
    dates = [start_date + timedelta(days=d) for d in range(delta.days+1)]

    #Create a bdata frame with dates with all values equal 0
    df_dates = pd.DataFrame({"Date":dates})
    df_dates["Number of Activities Planned"]=0
    df_dates["Total Duration of Activities Planned"]=0
    df_dates["Number of Planned Activities Marked Completed"]=0
    df_dates["Subject ID"] = username
    df_dates = df_dates.set_index(["Subject ID","Date"])

    #Get all plans for participant
    plans = ActivityPlan.objects.filter(user_id=uid).all().values('user_id', 'type_id', 'vigorous', 'start', 'date', 'timeOfDay', 'duration', 'created_at', 'updated_at', 'activity_log_id')
    
    if(len(plans)>0):    

        #Convert plans
        df_plans = pd.DataFrame.from_records(plans)

        #Make fields for each individual planned activity
        df_plans["creation_date"] = df_plans["created_at"].dt.date
        df_plans["activity_date"] = df_plans["start"].dt.date
        df_plans["marked_complete"] = df_plans["activity_log_id"].map(lambda x: x is not None)
        df_plans['Subject ID'] = df_plans["user_id"]
        df_plans['number_planned'] = 1
        df_plans = df_plans[["creation_date", "activity_date", 'number_planned', "duration", "marked_complete"]]

        #Group by date and sum to get totals by date
        plan_creation = df_plans.groupby("creation_date").sum()
        plan_creation["Subject ID"] = username
        plan_creation = plan_creation.reset_index()
        plan_creation = plan_creation.rename(columns={"creation_date":"Date"})

        #Add subject ID and re-label columns
        plan_creation = plan_creation.set_index(["Subject ID","Date"])
        plan_creation = plan_creation[["number_planned", "duration", "marked_complete"]]
        plan_creation = plan_creation.rename(columns={'number_planned':"Number of Activities Planned", "duration":"Total Duration of Activities Planned","marked_complete":"Number of Planned Activities Marked Completed"})

        #Combine with zeros data frame based on counts.
        #Duplicate days delt with using groupby on date and sum
        plan_creation_extended = pd.concat([df_dates,plan_creation],axis=0) 
        plan_creation_extended=plan_creation_extended.groupby(["Subject ID", "Date"]).sum()

        print(plan_creation)
    else:
        plan_creation_extended=df_dates
    
    plan_creation_extended.to_csv(os.path.join(directory,filename))
