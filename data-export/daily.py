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

from morning_messages.models import MorningMessage

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

    else:
        print('  EMPTY QUERY -- no messages found')
        plan_creation_extended=df_dates
    
    plan_creation_extended.to_csv(os.path.join(directory,filename))
    if(DEBUG):
        print("  Wrote %d rows"%(len(plan_creation_extended)))

def export_daily_morning_survey(user,directory = None, filename = None, start=None, end=None, from_scratch=True, DEBUG=True):

    """
    Construct dataframe from MorningMessage data model and export to csv
    Reference task: export_morning_message_survey in server/morning_messages/tasks.py
    """

    uid = user["uid"]
    username = user["hsid"]

    if DEBUG:
        print("  Exporting daily morning survey data for: ", username)

    # Export Destination
    if not directory:
        directory = './'
    if not filename:
        filename = '{username}.daily_morning_survey.csv'.format(
            username=username
        )

    # Skip rewriting if exists and trusted (no new data)
    if not from_scratch and os.path.isfile(os.path.join(directory, filename)):
        return

    # Get all weeks where participant may have received survey
    week_query = Week.objects.filter(user=uid).all().values('start_date', 'end_date')
    start_date = min([week["start_date"] for week in week_query])
    end_date = max([week["end_date"] for week in week_query])
    delta = end_date - start_date
    dates = [start_date + timedelta(days=d) for d in range(delta.days + 1)]

    days = Day.objects.filter(user_id=uid).order_by("date").all()
    day_lookup = {x.date: x.timezone for x in days}
    tzs = [day_lookup[date] if date in day_lookup else np.nan for date in dates ] 

    # Create a dataframe with each day in range and hsid
    df_dates = pd.DataFrame({"Date": dates})
    df_dates["Participant ID"] = username

    # Model Structure: MorningMessage -> MorningMessageSurvey -> Survey -> Q/A
    # Query all MorningMessages for user
    morning_messages = MorningMessage.objects \
        .order_by('date') \
        .filter(
            user=uid
        ) \
        .prefetch_decision() \
        .prefetch_message() \
        .prefetch_survey() \
        .prefetch_timezone() \
        .all()

    # toggle for debugging
    #code.interact(local=dict(globals(), **locals()))

    # MorningMessage question names for consistent headers across all users
    questions_headers = ['busy', 'rested', 'committed', 'mm_extrinsic_motivation', 'extrinsic', 'mm_intrinsic_motivation', 'intrinsic']

    # Construct DataFrame
    if len(morning_messages) > 1:

        # Map each time attribute if exists, otherwise np.nan
        df_morning_messages = pd.DataFrame({'Object': [msg for msg in morning_messages]})
        df_morning_messages['Date'] = df_morning_messages['Object'].map(lambda msg: msg.date)

        #df_morning_messages['Message Was Sent'] = df_morning_messages['Object'].map(lambda msg: bool(msg.message.sent) if msg.message is not None else 'False')
        #df_morning_messages['Message Was Opened'] = df_morning_messages['Object'].map(lambda msg: bool(msg.message.opened) if msg.message is not None else 'False')
        #df_morning_messages['Survey Was Answered'] = df_morning_messages['Object'].map(lambda msg: msg.survey.answered if msg.survey is not None else 'False')

        #df_morning_messages['Morning Message Sent Time'] = df_morning_messages['Object'].map(lambda msg: map_time_if_exists(msg.message.sent, msg.timezone) if msg.message is not None else np.nan)
        #df_morning_messages['Morning Message Received Time'] = df_morning_messages['Object'].map(lambda msg: map_time_if_exists(msg.message.received, msg.timezone) if msg.message is not None else np.nan)
        #df_morning_messages['Morning Message Opened Time'] = df_morning_messages['Object'].map(lambda msg: map_time_if_exists(msg.message.opened, msg.timezone) if msg.message is not None else np.nan)

        #df_morning_messages['Time Survey Created'] = df_morning_messages['Object'].map(lambda msg: map_time_if_exists(msg.survey.created, msg.timezone) if msg.survey is not None else np.nan)

        #Try mapping survey open and close times
        sdt = utils.estimate_survey_dwell_times(uid,survey_type="morning")
        survey_open_map = lambda msg: map_time_if_exists(sdt[msg.date]["opened"],msg.timezone) if msg.date in sdt else np.nan
        survey_close_map = lambda msg: map_time_if_exists(sdt[msg.date]["closed"] ,msg.timezone) if msg.date in sdt else np.nan

        msot = df_morning_messages['Object'].map(survey_open_map)
        msat = df_morning_messages['Object'].map(lambda msg: map_time_if_exists(msg.survey.answered_at, msg.timezone) if (msg.survey is not None and msg.survey.answered) else np.nan)

        df_morning_messages['Morning Survey Was Opened'] = msot.apply(lambda x: x is not np.nan)
        df_morning_messages['Morning Survey Was Answered'] = msat.apply(lambda x: x is not np.nan)

        df_morning_messages['Morning Survey Opened Time'] = msot
        #df_morning_messages['Time Survey Closed'] = df_morning_messages['Object'].map(survey_close_map)
        df_morning_messages['Morning Survey Answered Time'] = msat
        df_morning_messages['Morning Survey Time Spent Answering'] = df_morning_messages['Time Survey Answered'] - df_morning_messages['Time Survey Opened']

        #df_indicators = df_morning_messages[['Date']]
        #df_indicators['Morning Message Was Sent'] = df_morning_messages['Morning Message Sent Time'] .apply(lambda x: x is not np.nan)
        #df_indicators['Morning Message Was Received'] = df_morning_messages['Morning Message Received Time'].apply(lambda x: x is not np.nan)
        #df_indicators['Morning Message Was Opened'] = df_morning_messages['Morning Message Opened Time'].apply(lambda x: x is not np.nan)
        #df_morning_messages['Morning Survey Was Opened'] = msot.apply(lambda x: x is not np.nan)
        #df_morning_messages['Morning Survey Was Answered'] = msat.apply(lambda x: x is not np.nan)

        # Map each question to response title if answered
        for question in questions_headers:
            df_morning_messages[question.title()] = df_morning_messages['Object'].map(lambda msg: map_dict_if_key_exists(msg.survey.get_answers(), question) if msg.survey is not None else np.nan)

        # Merge intrinsic/extrinsic columns (old and new question)
        df_morning_messages['extrinsic'.title()] = df_morning_messages['extrinsic'.title()].combine_first(df_morning_messages['mm_extrinsic_motivation'.title()])
        df_morning_messages['intrinsic'.title()] = df_morning_messages['intrinsic'.title()].combine_first(df_morning_messages['mm_intrinsic_motivation'.title()])

        # Collect mood from answers dictionary
        df_morning_messages['Mood'] = df_morning_messages['Object'].map(lambda msg: map_dict_if_key_exists(msg.survey.get_answers(), 'selected_word') if msg.survey is not None else np.nan)

        # Drop 'Object' column
        df_morning_messages.drop('Object', axis=1, inplace=True)

        #Keep last morning message entry for each date if there are spurious duplicates
        df_morning_messages = utils.deduplicate_dates(df_morning_messages,"Date")

        # Outer join df_dates to include participant duration of study
        result = df_dates.join(df_morning_messages.set_index('Date'), on="Date", how="outer")
    

        import code
        code.interact(local=dict(globals(), **locals()))

    else:
        print('  EMPTY QUERY -- no data found')

        df_dates[['Time Sent', 'Time Received', 'Time Opened', 'Time Completed']] = np.nan

        df_dates[[question.title() for question in questions_headers]] = np.nan

        df_dates['Mood'] = np.nan
        result = df_dates

    # Drop extra intrinsic/extrinsic columns
    result.drop('mm_extrinsic_motivation'.title(), axis=1, inplace=True)
    result.drop('mm_intrinsic_motivation'.title(), axis=1, inplace=True)

    # Set Date as index of DataFrame
    result.set_index('Date').to_csv(os.path.join(directory, filename))

    if DEBUG:
        print("  Wrote %d rows" % (len(result)))


def map_time_if_exists(df_field, tz):
    return to_time(df_field.astimezone(tz).replace(tzinfo=None)) if df_field is not None else np.nan

def to_time(df_datetime):
    return df_datetime.strftime('%Y-%m-%d %H:%M:%S')

def map_dict_if_key_exists(d, key):
    return d[key] if d is not None and key in d.keys() and d[key] is not None else np.nan