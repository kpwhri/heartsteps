import datetime
import os
import shutil
import subprocess
import csv
from datetime import date
from datetime import timedelta
from math import floor

from django.db.models.query_utils import Q
from daily_step_goals.models import StepGoal
import pytz

from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.core import serializers

from activity_logs.tasks import export_activity_logs
from activity_surveys.tasks import export_activity_surveys
from adherence_messages.tasks import export_daily_metrics
from anti_sedentary.tasks import export_anti_sedentary_decisions
from anti_sedentary.tasks import export_anti_sedentary_service_requests
from days.models import Day
from days.services import DayService
from contact.models import ContactInformation
from fitbit_activities.models import FitbitDay
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_activities.models import FitbitMinuteHeartRate
from fitbit_activities.tasks import export_fitbit_data
from fitbit_activities.tasks import export_missing_fitbit_data
from fitbit_api.models import FitbitAccount
from fitbit_api.models import FitbitAccountUser
from locations.models import Location
from locations.models import Place
from locations.services import LocationService
from locations.tasks import export_location_count_csv
from locations.tasks import update_location_categories
from morning_messages.tasks import export_morning_message_survey
from morning_messages.tasks import export_morning_messages
from page_views.models import PageView
from push_messages.models import Message as PushMessage
from walking_suggestion_surveys.tasks import export_walking_suggestion_surveys
from walking_suggestions.models import Configuration as WalkingSuggestionConfiguration
from walking_suggestions.tasks import export_walking_suggestion_decisions
from walking_suggestions.tasks import export_walking_suggestion_service_requests
from watch_app.tasks import export_step_count_records_csv
from weekly_reflection.models import ReflectionTime
from user_event_logs.models import EventLog

from .services import ParticipantService
from .models import Cohort, User
from .models import DataExport
from .models import DataExportSummary
from .models import DataExportQueue
from .models import Study
from .models import Participant


def force_convert(obj):
    if obj is None:
        return '""'
    elif isinstance(obj, int):
        return '"{}"'.format(str(obj))
    elif isinstance(obj, bool):
        return '"{}"'.format(str(obj))
    elif isinstance(obj, str):
        return '"{}"'.format(str(obj))
    elif isinstance(obj, datetime.datetime):
        return '"{}"'.format(obj.strftime("%Y-%m-%d %H:%M:%S.%f"))
    elif isinstance(obj, datetime.date):
        return '"{}"'.format(obj.strftime("%Y-%m-%d"))
    elif isinstance(obj, dict):
        str_list = []
        for key, val in obj.items():
            str_list.append('"{}": {}'.format(key, force_convert(val)))
        return '{{}}'.format(", ".join(str_list))
    elif isinstance(obj, list):
        return '"{}"'.format(str([force_convert(x) for x in obj]))
    else:
        return '"{}"'.format(str(obj))

@shared_task
def reset_test_participants(date_joined=None, number_of_days=9):
    current_year = date.today().strftime('%Y')

    study, _ = Study.objects.get_or_create(name='Test')
    cohort, _ = Cohort.objects.get_or_create(
        name="test",
        study=study
    )

    try:
        participant = Participant.objects.get(heartsteps_id='test-new')
        participant.delete()
    except Participant.DoesNotExist:
        pass
    Participant.objects.create(
        heartsteps_id='test-new',
        enrollment_token='test-new1',
        birth_year=current_year,
        cohort=cohort
    )

    try:
        participant = Participant.objects.get(heartsteps_id='test')
        participant.delete()
    except Participant.DoesNotExist:
        pass
    participant = Participant.objects.create(
        heartsteps_id='test',
        enrollment_token='test-test',
        birth_year=current_year,
        cohort=cohort
    )

    participant_service = ParticipantService(participant=participant)
    participant_service.initialize()

    participant = Participant.objects.get(heartsteps_id='test')
    user = participant.user

    user.is_staff = True
    user.save()

    ContactInformation.objects.update_or_create(
        user=user,
        defaults={
            'name': 'Testy test',
            'email': 'test@nickreid.com',
            'phone': '5555555555'
        }
    )

    fitbit_account, _ = FitbitAccount.objects.get_or_create(
        fitbit_user='test'
    )
    FitbitAccountUser.objects.update_or_create(
        user=user,
        defaults={
            'account': fitbit_account
        }
    )

    Place.objects.create(
        user=user,
        type=Place.HOME,
        address='Space Needle, Seattle, Washington, United States of America',
        latitude=47.6205,
        longitude=-122.34899999999999
    )
    Place.objects.create(
        user=user,
        type=Place.WORK,
        address='1730 Minor Avenue, Seattle, Washington, United States of America',
        latitude=47.6129,
        longitude=-122.327
    )
    ws_configuration, _ = WalkingSuggestionConfiguration.objects.update_or_create(
        user=user,
        defaults={
            'enabled': True
        }
    )
    ws_configuration.set_default_walking_suggestion_times()
    ReflectionTime.objects.update_or_create(
        user=user,
        defaults={
            'day': 'sunday',
            'time': '19:00'
        }
    )

    # Clear and re-create activity data
    Day.objects.filter(user=user).all().delete()
    FitbitDay.objects.filter(account=fitbit_account).all().delete()

    location_service = LocationService(user=user)
    tz = location_service.get_home_timezone()
    current_dt = location_service.get_home_current_datetime()

    if date_joined:
        user.date_joined = date_joined
    else:
        user.date_joined = current_dt - timedelta(days=number_of_days)
    user.save()
    date_joined = date(
        user.date_joined.year,
        user.date_joined.month,
        user.date_joined.day
    )

    dates_to_create = [
        date_joined + timedelta(days=offset) for offset in range(number_of_days)]
    dates_to_create.append(
        date(current_dt.year, current_dt.month, current_dt.day))
    for _date in dates_to_create:
        day, _ = FitbitDay.objects.update_or_create(
            account=fitbit_account,
            date=_date,
            defaults={
                '_timezone': tz.zone,
                'step_count': 2000,
                '_distance': 2,
                'wore_fitbit': True
            }
        )
        # Add heartrate for every minute of the day
        dt = day.get_start_datetime()
        day_end = dt.replace(hour=20)
        while dt < day_end:
            FitbitMinuteHeartRate.objects.create(
                account=fitbit_account,
                time=dt,
                heart_rate=1234
            )
            dt = dt + timedelta(minutes=1)
        day.save()

        Day.objects.update_or_create(
            user=user,
            date=_date,
            defaults={
                'timezone': tz.zone
            }
        )


def initialize_test_participant():
    try:
        participant = Participant.objects.get(heartsteps_id='test')
        participant_service = ParticipantService(participant=participant)
        participant_service.initialize()
    except Participant.DoesNotExist:
        print('ERROR FROM INITIALIZE_TEST_PARTICIPANT: participant does not exist')


def format_datetime(dt, tz=None):
    if dt:
        if tz:
            dt = dt.astimezone(tz)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return None


def export_user_messages(username, directory=None, filename=None, start=None, end=None):
    if not directory:
        directory = './'
    if not filename:
        filename = '%s.messages.csv' % (username)

    push_messages_query = PushMessage.objects.filter(
        recipient__username=username,
        message_type=PushMessage.NOTIFICATION
    ) \
        .order_by('created')
    if start:
        push_messages_query = push_messages_query.filter(
            created__gte=start
        )
    if end:
        push_messages_query = push_messages_query.filter(
            created__lte=end
        )

    messages = []

    days = Day.objects.filter(user__username=username).order_by('date').all()
    days = list(days)
    current_day = None
    if days:
        current_day = days.pop(0)
        for push_message in push_messages_query.all():
            print(push_message.uuid, push_message.created)
            while days and current_day and push_message.created > current_day.end:
                current_day = days.pop(0)
                print(current_day.date, current_day.timezone)

            messages.append([
                username,
                str(push_message.uuid),
                push_message.collapse_subject,
                push_message.title,
                push_message.body,
                format_datetime(push_message.sent, current_day.get_timezone()),
                format_datetime(push_message.received,
                                current_day.get_timezone()),
                format_datetime(push_message.opened,
                                current_day.get_timezone()),
                format_datetime(push_message.engaged,
                                current_day.get_timezone())
            ])
    _file = open(os.path.join(directory, filename), 'w')
    writer = csv.writer(_file)
    writer.writerows(
        [[
            'HeartSteps ID',
            'Message ID',
            'Message Type'
            'Notification Title',
            'Notification Text',
            'Message Sent',
            'Message Received',
            'Message Opened',
            'Message Engaged'
        ]] + messages
    )
    _file.close()

def export_daily_step_goals(username, directory=None, filename=None, start=None, end=None):
    if not directory:
        directory = './'
    if not filename:
        filename = '%s.daily-step-goals.csv' % (username)

    user = User.objects.get(username=username)
    daily_step_goals_query = StepGoal.objects.filter(
        user=user
    ).order_by('date', '-created')
    
    if start:
        daily_step_goals_query = daily_step_goals_query.filter(
            date__gte=start
        )
    if end:
        daily_step_goals_query = daily_step_goals_query.filter(
            date__lte=end
        )

    goal_matrix = [
        [
            force_convert(username),
            force_convert(x.uuid),
            force_convert(x.date),
            force_convert(x.created),
            force_convert(x.step_goal)
         ] for x in daily_step_goals_query.all()
    ]
        
    _file = open(os.path.join(directory, filename), 'w')
    writer = csv.writer(_file)
    writer.writerows(
        [[
            'HeartSteps ID',
            'Step Goal ID',
            'Date',
            'Goal Calculation Time',
            'Goal'
        ]] + goal_matrix
    )
    _file.close()
    
    
def export_bout_planning_decisions(username, directory=None, filename=None, start=None, end=None):
    from bout_planning_notification.models import BoutPlanningDecision
    
    if not directory:
        directory = './'
    if not filename:
        filename = '%s.bout-planning-decisions.csv' % (username)

    user = User.objects.get(username=username)
    
    query = BoutPlanningDecision.objects.filter(
        user=user
    ).order_by('-when_created')
    
    if start:
        query = query.filter(
            when_created__gte=start
        )
    if end:
        query = query.filter(
            when_created__lte=end
        )
        
    data_matrix = [
        [username,
         force_convert(x.id),
         force_convert(x.N),
         force_convert(x.O),
         force_convert(x.R),
         force_convert(x.return_bool),
         force_convert(x.when_created),
         force_convert(x.data)
         ] for x in query.all()
    ]
        
    _file = open(os.path.join(directory, filename), 'w')
    writer = csv.writer(_file)
    writer.writerows(
        [[
            'HeartSteps ID',
            'BoutPlanningDecision ID',
            'Need',
            'Opportunity',
            'Receptivity',
            'Is Notificaion Sent',
            'Calculation Time',
            'Supporting Data'
        ]] + data_matrix
    )
    _file.close()

def export_survey_responses(username, directory=None, filename=None, start=None, end=None):
    from surveys.models import Survey, SurveyResponse
    
    if not directory:
        directory = './'
    if not filename:
        filename = '%s.export-survey-responses.csv' % (username)

    user = User.objects.get(username=username)
    
    query = Survey.objects.filter(
        user=user
    ).order_by('-created')
    
    if start:
        query = query.filter(
            created__gte=start
        )
    if end:
        query = query.filter(
            created__lte=end
        )
        
    data_matrix = []
    
    def get_response_vector(response=None, survey=None, title=False):
        response_vector = ['']
        survey_vector = [''] * 5
        question_origin_vector = [''] * 9
        question_vector = [''] * 5
        answer_origin_vector = [''] * 5
        answer_vector = [''] * 3
        
        if title:
            response_vector = ["response.id"]
            survey_vector = ["survey.uuid",
                "survey.user.username",
                "survey.answered",
                "survey.created",
                "survey.updated"
                ]
            question_origin_vector = [
                "question_origin.name",
                "question_origin.label",
                "question_origin.description",
                "question_origin.kind",
                "question_origin.published",
                "question_origin.order",
                "question_origin.created",
                "question_origin.updated",
                "question_origin.order"
                ]
            question_vector = [
                "question.order",
                "question.name",
                "question.label",
                "question.description",
                "question.kind"
                ]
            answer_origin_vector = [
                "answer_origin.label",
                "answer_origin.value",
                "answer_origin.order",
                "answer_origin.created",
                "answer_origin.updated"
                ]
            answer_vector = [
                "answer.label",
                "answer.value",
                "answer.order"
                ]
        else:
            if response:
                response_vector = [force_convert(response.id)]
            
                survey = response.survey
                if survey:
                    survey_vector = [
                        force_convert(survey.uuid),
                        force_convert(survey.user.username),
                        force_convert(survey.answered),
                        force_convert(survey.created),
                        force_convert(survey.updated)
                    ]
                    question = response.question
                    if question:
                        question_vector = [
                            force_convert(question.order),
                            force_convert(question.name),
                            force_convert(question.label),
                            force_convert(question.description),
                            force_convert(question.kind)
                        ]
                        question_origin = question.question
                        if question_origin:
                            question_origin_vector = [
                                force_convert(question_origin.name),
                                force_convert(question_origin.label),
                                force_convert(question_origin.description),
                                force_convert(question_origin.kind),
                                force_convert(question_origin.published),
                                force_convert(question_origin.order),
                                force_convert(question_origin.created),
                                force_convert(question_origin.updated),
                                force_convert(question_origin.order)
                            ]
                    answer = response.answer
                    if answer:
                        answer_vector = [
                            force_convert(answer.label),
                            force_convert(answer.value),
                            force_convert(answer.order)
                        ]
                        answer_origin = answer.answer
                        if answer_origin:
                            answer_origin_vector = [
                                force_convert(answer_origin.label),
                                force_convert(answer_origin.value),
                                force_convert(answer_origin.order),
                                force_convert(answer_origin.created),
                                force_convert(answer_origin.updated)
                            ]
            else:
                # if survey is not responded, return survey info only
                survey_vector = [
                    force_convert(survey.uuid),
                    force_convert(survey.user.username),
                    force_convert(survey.answered),
                    force_convert(survey.created),
                    force_convert(survey.updated)
                ]
                
        return response_vector + survey_vector + question_origin_vector + question_vector + answer_origin_vector + answer_vector
    
    
    for survey in list(query.all()):
        
        response_query = SurveyResponse.objects.filter(survey=survey).order_by('question__order', 'answer__value')
        
        if response_query.exists():
            for response in list(response_query.all()):
                data_matrix.append(
                    get_response_vector(response)
                )
        else:
            # if the participant did not respond
            data_matrix.append(
                get_response_vector(survey=survey)
            )
        
    _file = open(os.path.join(directory, filename), 'w')
    writer = csv.writer(_file)
    writer.writerows(
        [
            get_response_vector(title=True)
        ] + data_matrix
    )
    _file.close()

def export_app_page_views(username, directory=None, filename=None, start=None, end=None):
    if not directory:
        directory = './'
    if not filename:
        filename = '%s.page_views.csv' % (username)

    page_views_query = PageView.objects.filter(
        user__username=username
    ).exclude(platform=PageView.WEBSITE)
    days_query = Day.objects.filter(
        user__username=username
    )
    if start:
        page_views_query = page_views_query.filter(
            time__gte=start
        )
        days_query = days_query.filter(
            end__gte=start
        )
    if end:
        page_views_query = page_views_query.filter(
            time__lte=end
        )
        days_query = days_query.filter(
            start__lte=end
        )
    days = days_query.order_by('start').all()
    days = list(days)
    current_day = None
    current_timezone = pytz.UTC
    if days:
        current_day = days.pop(0)
        current_timezone = current_day.get_timezone()

    page_views = []
    for page_view in page_views_query.order_by('time').all():
        if current_day and days:
            while current_day.end < page_view.time and days:
                current_day = days.pop(0)
        page_view_time = page_view.time.astimezone(current_timezone)
        page_views.append([
            username,
            page_view_time.strftime('%Y-%m-%d'),
            page_view_time.strftime('%H:%M:%S'),
            current_timezone.zone,
            page_view.uri
        ])
    _file = open(os.path.join(directory, filename), 'w')
    writer = csv.writer(_file)
    writer.writerows(
        [[
            'HeartSteps ID',
            'Date',
            'Time',
            'Timezone',
            'Uri'
        ]] + page_views
    )
    _file.close()


def export_user_locations(username, directory=None, filename=None, start=None, end=None):
    if not directory:
        directory = './'
    if not filename:
        filename = '%s.locations.csv' % (username)

    locations_query = Location.objects.filter(user__username=username)
    if start:
        locations_query = locations_query.filter(
            time__gte=start
        )
    if end:
        locations_query = locations_query.filter(
            time__lte=end
        )

    locations = []
    for _location in locations_query.order_by('time').all():
        locations.append([
            _location.id,
            username,
            _location.local_time.strftime('%Y-%m-%d %H:%M:%S'),
            _location.timezone.zone,
            _location.source,
            _location.category
        ])
    _file = open(os.path.join(directory, filename), 'w')
    writer = csv.writer(_file)
    writer.writerows(
        [[
            'ID',
            'HeartSteps ID',
            'Time',
            'Timezone',
            'Location Source',
            'Location Category'
        ]] + locations
    )
    _file.close()


def setup_exports(participant, directory, log_export=True):
    def export_file(fn, filename):
        filename = '{study}.{cohort}.{heartsteps_id}.{filename}'.format(
            filename=filename,
            heartsteps_id=participant.heartsteps_id,
            cohort=participant.cohort.slug,
            study=participant.cohort.study.slug
        )

        start = participant.study_start
        end = participant.study_end
        if end > timezone.now():
            end = timezone.now()

        if log_export:
            print('Export start: {}'.format(filename))
            export = DataExport(
                user=participant.user,
                filename=filename,
                start=timezone.now()
            )
            try:
                fn(
                    username=participant.user.username,
                    filename=filename,
                    directory=directory,
                    start=start,
                    end=end
                )
            except Exception as e:
                print('Error:', e)
                export.error_message = e
            export.end = timezone.now()
            export.save()

            summary, _ = DataExportSummary.objects.get_or_create(
                user=participant.user,
                category=export.category
            )
            summary.last_data_export = export
            summary.save()

            diff = export.end - export.start
            minutes = floor(diff.seconds/60)
            seconds = diff.seconds - (minutes*60)
            print('Export end: {} ({} minutes {} seconds)'.format(
                filename, minutes, seconds))
        else:
            start = timezone.now()
            print('Export start: {}'.format(filename))
            fn(
                username=participant.user.username,
                filename=filename,
                directory=directory,
                start=start,
                end=end
            )
            end = timezone.now()
            diff = end - start
            minutes = floor(diff.seconds/60)
            seconds = diff.seconds - (minutes*60)
            print('Export end: {} ({} minutes {} seconds)'.format(
                filename, minutes, seconds))
    return export_file


def export_single_file(username, log_export=True):
    print("Getting authenticated...")
    # getting authenticated
    subprocess.call(
        'gcloud auth activate-service-account --key-file=/credentials/gcloud-dev-service-account.json', 
        shell=True
    )    
    
    participant = Participant.objects.get(user__username=username)
    cohort = participant.cohort
    if not cohort or not cohort.export_bucket_url:
        return False

    EXPORT_DIRECTORY = '/heartsteps-export'
    if log_export:
        # reset the export directory (if it exists, this code removes it)
        if not os.path.exists(EXPORT_DIRECTORY):
            os.makedirs(EXPORT_DIRECTORY)
        directory = os.path.join(EXPORT_DIRECTORY, username)
        if os.path.exists(directory) and os.path.isdir(directory):
            shutil.rmtree(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
    else:
        directory = './'

    print("    preparing export_file fx")
    export_file = setup_exports(participant, directory, log_export)

    print("    export_daily_step_goals")
    export_file(export_daily_step_goals,
                filename='daily-step-goals.csv')
    
    print("    export_bout_planning_decisions")
    export_file(export_bout_planning_decisions,
                filename='bout-planning-decisions.csv')
    
    print("    export_survey_response")
    export_file(export_survey_responses,
                filename='survey-responses.csv')

    if log_export:
        subprocess.call(
            'gsutil -m rsync %s gs://%s' % (directory,
                                            cohort.export_bucket_url),
            shell=True
        )


@shared_task
def export_user_data(username, log_export=True):
    print("    export_user_data: {}".format(username))
    
    participant = Participant.objects.get(user__username=username)
    cohort = participant.cohort
    if not cohort or not cohort.export_bucket_url:
        return False

    EXPORT_DIRECTORY = '/heartsteps-export'
    if log_export:
        # reset the export directory (if it exists, this code removes it)
        if not os.path.exists(EXPORT_DIRECTORY):
            os.makedirs(EXPORT_DIRECTORY)
        directory = os.path.join(EXPORT_DIRECTORY, username)
        if os.path.exists(directory) and os.path.isdir(directory):
            shutil.rmtree(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
    else:
        directory = './'

    print("    preparing export_file fx")
    export_file = setup_exports(participant, directory, log_export)

    print("    export_activity_logs")
    export_file(export_activity_logs,
                filename='activity-logs.csv'
                )
    print("    export_activity_surveys")
    export_file(export_activity_surveys,
                filename='activity-surveys.csv'
                )
    print("    export_anti_sedentary_decisions")
    export_file(export_anti_sedentary_decisions,
                filename='anti-sedentary-decisions.csv'
                )
    print("    export_anti_sedentary_service_requests")
    export_file(export_anti_sedentary_service_requests,
                filename='anti-sedentary-service-requests.csv'
                )
    print("    export_daily_metrics")
    export_file(export_daily_metrics,
                filename='daily-metrics.csv'
                )
    print("    export_fitbit_data")
    export_file(export_fitbit_data,
                filename='fitbit-data-per-minute.csv'
                )
    print("    export_user_locations")
    export_file(export_user_locations,
                filename='locations.csv'
                )
    print("    export_morning_messages")
    export_file(
        export_morning_messages,
        filename='morning-messages.csv'
    )
    print("    export_morning_message_survey")
    export_file(
        export_morning_message_survey,
        filename='morning-survey.csv'
    )
    print("    export_walking_suggestion_decisions")
    export_file(export_walking_suggestion_decisions,
                filename='walking-suggestion-decisions.csv'
                )
    print("    export_walking_suggestion_service_requests")
    export_file(export_walking_suggestion_service_requests,
                filename='walking-suggestion-service-requests.csv'
                )
    print("    export_walking_suggestion_surveys")
    export_file(export_walking_suggestion_surveys,
                filename='walking-suggestion-surveys.csv'
                )
    print("    export_app_page_views")
    export_file(export_app_page_views,
                filename='client-page-views.csv'
                )
    print("    export_user_messages")
    export_file(export_user_messages,
                filename='messages.csv'
                )
    print("    export_daily_step_goals")
    export_file(export_daily_step_goals,
                filename='daily-step-goals.csv')
    
    print("    export_bout_planning_decisions")
    export_file(export_bout_planning_decisions,
                filename='bout-planning-decisions.csv')
    
    print("    export_survey_response")
    export_file(export_survey_responses,
                filename='survey-responses.csv')

    if log_export:
        subprocess.call(
            'gsutil -m rsync %s gs://%s' % (directory,
                                            cohort.export_bucket_url),
            shell=True
        )


@shared_task
def export_cohort_data():
    EventLog.info(None, 'export_cohort_data is running')
    print("Getting authenticated...")
    # getting authenticated
    subprocess.call(
        'gcloud auth activate-service-account --key-file=/credentials/gcloud-dev-service-account.json', 
        shell=True
    )    
    
    for cohort in Cohort.objects.filter(export_data=True).all():
        print("Cohort {}:".format(cohort.name))
        participants = Participant.objects.filter(cohort=cohort) \
            .prefetch_related('user') \
            .all()
        users = [p.user for p in participants if p.user]
        for user in users:
            print("  User {}:".format(user.username))
            export_user_data.apply_async(kwargs={
                'username': user.username
            })
            # export_user_data(user.username)


@shared_task
def daily_update(username):
    service = ParticipantService(username=username)
    day_service = DayService(username=username)
    yesterday = day_service.get_current_date() - timedelta(days=1)
    service.update(yesterday)
    if not service.participant.study_start_date:
        service.participant.study_start_date = service.participant.get_study_start_date()
        service.participant.save()
    update_location_categories(username)


@shared_task
def process_data_export_queue():
    queued_data_exports = DataExportQueue.objects.filter(
        started=None
    ).all()
    for queued_export in queued_data_exports:
        export_user_data.apply_async(kwargs={
            'username': queued_export.user.username
        })
        queued_export.started = timezone.now()
        queued_export.save()


def serialize_user_information(heartsteps_ids, filename='export.json'):
    participants = Participant.objects.filter(
        heartsteps_id__in=heartsteps_ids
    ).all()
    for participant in participants:
        # Removing but not saving cohort information
        # because we don't care about serializing
        # survey administration data
        participant.cohort = None
    users = [p.user for p in participants if p.user]

    fitbit_account_users = FitbitAccountUser.objects.filter(user__in=users) \
        .prefetch_related('account') \
        .all()
    fitbit_accounts = []
    for au in fitbit_account_users:
        if au.account.uuid not in [account.uuid for account in fitbit_accounts]:
            au.account.fitbit_user = str(au.account.uuid)[:10]
            au.account.access_token = None
            au.account.refresh_token = None
            au.account.expires_at = None
            fitbit_accounts.append(au.account)
    fitbit_days = FitbitDay.objects.filter(account__in=fitbit_accounts).all()
    fitbit_heart_rate_minutes = FitbitMinuteHeartRate.objects.filter(
        account__in=fitbit_accounts).all()
    fitbit_step_count_minutes = FitbitMinuteStepCount.objects.filter(
        account__in=fitbit_accounts).all()

    objects = []
    for queryset in [users, participants, fitbit_accounts, fitbit_account_users, fitbit_days, fitbit_heart_rate_minutes, fitbit_step_count_minutes]:
        objects += list(queryset)

    json = serializers.serialize('json', objects)
    print(type(json), len(json))
    _file = open(filename, 'w')

    total_length = len(json)
    position = 0
    while position < total_length:
        end_position = position + 1000
        if end_position >= total_length:
            end_position = total_length

        _file.write(json[position:end_position])

        position = end_position
    _file.close()
