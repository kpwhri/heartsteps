from days.services import DayService
from feature_flags.models import FeatureFlags
from participants.models import Participant
from participants.services import ParticipantService
from surveys.serializers import SurveySerializer, SurveyShirinker
from user_event_logs.models import EventLog
from push_messages.services import PushMessageService

from .models import BoutPlanningSurvey, Level, BoutPlanningDecision, BoutPlanningNotification, JustWalkJitaiDailyEma, LevelSequence, LevelSequence_User, User

class BoutPlanningNotificationService:
    class NotificationSendError(RuntimeError):
        pass

    def __init__(self, user):
        assert user is not None, "User must be specified"

        self.user = user
        self.level = None
        self.decision = None
        EventLog.debug(self.user, "Starting BoutPlanningNotificationService")

    def create_survey(self):
        bout_planning_survey = BoutPlanningSurvey.objects.create(user=self.user)
        bout_planning_survey.reset_questions()
        
        return bout_planning_survey
    
    def create_test_survey(self):
        return self.create_survey()
    
    def create_daily_ema(self):
        daily_ema_survey = JustWalkJitaiDailyEma.objects.create(user=self.user)
        daily_ema_survey.reset_questions()
        
        return daily_ema_survey
    
    def has_sequence_assigned(self):
        return LevelSequence_User.objects.filter(user=self.user).exists()
        
    def is_necessary(self):
        EventLog.debug(self.user, "is_necessary() is called")
        self.decision = BoutPlanningDecision.create(self.user)
        self.decision.add_line("BoutPlanningDecision object is created")
        
        self.decision.add_line("Checking if the user is in baseline period or not")
        participant_service = ParticipantService(user=self.user)
        if participant_service.is_baseline_complete():
            self.decision.add_line("The user is not in baseline period. moving on.")
        else:
            self.decision.add_line("The user is in baseline period. Returning False.")
            self.decision.save()
            return False
            
        day_service = DayService(self.user)
        
        self.decision.add_line("Starting is_necessary() calculation for {} @ {} (local)".format(self.user.username, day_service.get_current_datetime()))
        self.level = Level.get(self.user)
        self.decision.data["level"] = str(self.level.level)
        self.decision.add_line("Level '{}' is fetched from DB".format(self.level))
        
        if self.level.level == Level.RECOVERY:
            self.decision.add_line("Since the level is RECOVERY, no further processing will be done.")
            return_bool = False
        elif self.level.level == Level.RANDOM:
            self.decision.add_line("Since the level is RANDOM, apply_random is done.")
            self.decision.apply_random()
            return_bool = self.decision.decide()
        elif self.level.level == Level.NO:
            self.decision.add_line("Since the level is NO, apply_N and apply_O will be done.")
            self.decision.apply_N()
            self.decision.apply_O()
            return_bool = self.decision.decide()
        elif self.level.level == Level.NR:
            self.decision.add_line("Since the level is NR, apply_N and apply_R will be done.")
            self.decision.apply_N()
            self.decision.apply_R()
            return_bool = self.decision.decide()
        elif self.level.level == Level.FULL:
            self.decision.add_line("Since the level is FULL, apply_N, apply_O, and apply_R will be done.")
            self.decision.apply_N()
            self.decision.apply_O()
            self.decision.apply_R()
            return_bool = self.decision.decide()
        else:
            raise RuntimeError("Unsupported decision type: {}".format(self.level.level))
        self.decision.add_line("The decision is delivered: {}".format(return_bool))
        self.decision.save()
        return return_bool
    
    def send_notification(self,
                          title='Sample Bout Planning Title',
                          body='Sample Bout Planning Body.',
                          collapse_subject='bout_planninng',
                          survey=None,
                          data={}):
        try:
            EventLog.debug(self.user, "BoutPlanningNotificationService.send_notification()")
            if survey is not None:
                EventLog.debug(self.user, "BoutPlanningNotificationService.send_notification() - survey is not None")
                shrinked_survey = SurveyShirinker(survey)
                EventLog.debug(self.user, "BoutPlanningNotificationService.send_notification() - Survey is shrinked")
                data["survey"] = shrinked_survey.to_json()
                EventLog.debug(self.user, "{}".format(shrinked_survey.to_json()))
            
            service = PushMessageService(user=self.user)
            EventLog.debug(self.user)
            message = service.send_notification(
                body=body,
                title=title,
                collapse_subject=collapse_subject,
                data=data)
            EventLog.debug(self.user)
            BoutPlanningNotification.create(user=self.user, message=message, level=self.level, decision=self.decision)
            EventLog.debug(self.user)
            return message
        except (PushMessageService.MessageSendError,
                PushMessageService.DeviceMissingError) as e:
            raise BoutPlanningNotificationService.NotificationSendError(
                'Unable to send notification')

    def assign_level_sequence(self, cohort, user=None):
        # assign unused level sequences to all users without level sequences
        lines = []
        if user is None:
            participants = Participant.objects.filter(cohort=cohort)
            user_list_temp = [p.user.username for p in participants]
            user_list = User.objects.filter(username__in=user_list_temp)
            for user in user_list:
                if FeatureFlags.has_flag(user, "bout_planning"):
                    query = LevelSequence_User.objects.filter(user=user)
                    if query.exists():
                        # level sequence is already assigned
                        pass
                    else:
                        lines = lines + self.assign_level_sequence(cohort, user)
        else:
            # user is specified
            if FeatureFlags.has_flag(user, "bout_planning"):
                query = LevelSequence.objects.filter(cohort=cohort, is_used=False).order_by("order", "when_created")
                
                if query.exists():
                    # one or more level sequence is left
                    level_sequence = query.first()
                    assignment = LevelSequence_User.objects.create(user=user, level_sequence=level_sequence)
                    level_sequence.is_used = True
                    level_sequence.when_used = assignment.assigned
                    level_sequence.save()
                    
                    level_list = level_sequence.sequence_text.split(",")
                    level_list = [x.strip() for x in level_list]
                    
                    current_date = Participant.objects.filter(user=user).first().study_start_date + datetime.timedelta(days=cohort.study.baseline_period)
                    
                    level_objects = [Level.LEVELS[int(x)][0] for x in level_list]
                    Level.bulk_create(user, level_objects, current_date)
                    lines.append("The user '{}' is assigned to the sequence({})".format(user.username, level_sequence.order))
                else:
                    lines.append("No sequence is left. The user '{}' is not assigned to the sequence.".format(user.username))
            else:
                lines.append("The user '{}' does not have bout_planning feature flag.".format(user.username))
            lines.append(" ")
            
        return lines