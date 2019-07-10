import uuid, random
from datetime import datetime
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User

from behavioral_messages.models import MessageTemplate
from days.services import DayService
from fitbit_activities.services import FitbitStepCountService
from push_messages.models import Message
from push_messages.services import PushMessageService

class ContextTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=25)

    name = models.CharField(max_length=50, null=True, blank=True)
    dashboard = models.BooleanField(default=False)

    def __str__(self):
        return self.name or self.tag

class UnavailableReason(models.Model):

    UNREACHABLE = 'unreachable'
    NOTIFICATION_RECENTLY_SENT = 'notification-recently-sent'
    NOT_SEDENTARY = 'not-sedentary'
    ON_VACATION = 'on-vacation'
    NO_STEP_COUNT_DATA = 'no-step-count-data'
    DISABLED = 'disabled'
    SERVICE_ERROR = 'service-error'

    CHOICES = [
        (UNREACHABLE, 'Unreachable'),
        (NOTIFICATION_RECENTLY_SENT, 'Notification recently sent'),
        (NOT_SEDENTARY, 'Not sedentary'),
        (NO_STEP_COUNT_DATA, 'No step-count data'),
        (ON_VACATION, 'On vaaction'),
        (DISABLED, 'Disabled'),
        (SERVICE_ERROR, 'service-error')
    ]

    decision = models.ForeignKey(
        'randomization.Decision',
        on_delete = models.CASCADE
    )
    reason = models.CharField(max_length=150, choices=CHOICES)

class Decision(models.Model):

    MESSAGE_TEMPLATE_MODEL = MessageTemplate

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)

    test = models.BooleanField(default=False)
    imputed = models.BooleanField(default=False)
    available = models.NullBooleanField(null=True)
    sedentary = models.NullBooleanField(null=True)

    time = models.DateTimeField()

    treated = models.NullBooleanField(null=True, blank=True)
    treatment_probability = models.FloatField(null=True, blank=True)

    tags = models.ManyToManyField(ContextTag)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-time']

    def __get_unavailable_reason(self, reason):
        try:
            UnavailableReason.objects.get(
                decision = self,
                reason = reason
            )
            return True
        except UnavailableReason.DoesNotExist:
            return False

    def __set_unavailable_reason(self, reason, value):
        if value:
            UnavailableReason.objects.update_or_create(
                decision = self,
                reason = reason
            )
        else:
            try:
                reason = UnavailableReason.objects.get(
                    decision = self,
                    reason = reason
                )
                reason.delete()
            except UnavailableReason.DoesNotExist:
                pass

    def make_unavailable_property(reason):
        def get_reason(self):
            return self.__get_unavailable_reason(
                reason = reason
            )
        def set_reason(self, value):
            self.__set_unavailable_reason(
                reason = reason,
                value = value
            )
        return property(get_reason, set_reason)

    def update_available_value(self):
        reasons = UnavailableReason.objects.filter(
            decision = self
        ).count()
        if reasons > 0:
            self.available = False
        else:
            self.available = True

    unavailable_no_step_count_data = make_unavailable_property(UnavailableReason.NO_STEP_COUNT_DATA)
    unavailable_not_sedentary = make_unavailable_property(UnavailableReason.NOT_SEDENTARY)
    unavailable_notification_recently_sent = make_unavailable_property(UnavailableReason.NOTIFICATION_RECENTLY_SENT)
    unavailable_unreachable = make_unavailable_property(UnavailableReason.UNREACHABLE)
    unavailable_disabled = make_unavailable_property(UnavailableReason.DISABLED)
    unavailable_service_error = make_unavailable_property(UnavailableReason.SERVICE_ERROR)

    def get_treated(self):
        return self.treated
    
    def set_treated(self, value):
        self.treated = value

    a_it = property(get_treated, set_treated)

    def get_treatment_probability(self):
        return self.treatment_probability

    def set_treatment_probability(self, value):
        self.treatment_probability = value

    pi_it = property(get_treatment_probability, set_treatment_probability)

    def decide(self):
        if self.test:
            self.treated = True
            self.treatment_probability = 1
            self.save()
            return True
        if not self.available:
            self.a_it = False
            self.save()
            return self.a_it
        if not self.pi_it:
            if not hasattr(settings, 'RANDOMIZATION_FIXED_PROBABILITY'):
                raise ImproperlyConfigured("No RANDOMIZATION_FIXED_PROBABILITY")
            self.pi_it = settings.RANDOMIZATION_FIXED_PROBABILITY
        self.a_it = random.random() < self.pi_it
        self.save()
        return self.a_it

    @property
    def notification(self):
        if hasattr(self, '_notification'):
            return self._notification
        message_content_type = ContentType.objects.get_for_model(Message)
        context_objects = DecisionContext.objects.filter(
            decision = self,
            content_type = message_content_type
        ).all()
        for message in [obj.content_object for obj in context_objects]:
            if message.message_type == Message.NOTIFICATION:
                self._notification = message
                return self._notification
        return False

    @property
    def message_template(self):
        try:
            context_object = DecisionContext.objects.get(
                decision = self,
                content_type = ContentType.objects.get_for_model(self.MESSAGE_TEMPLATE_MODEL)
            )
            message_template = context_object.content_object
            return message_template
        except DecisionContext.DoesNotExist:
            return None

    def add_context_object(self, object):
        DecisionContext.objects.create(
            decision = self,
            content_object = object
        )

    def get_context(self):
        return [tag.tag for tag in self.tags.all()]

    def add_context(self, tag_text):
        tag, _ = ContextTag.objects.get_or_create(
            tag = tag_text
        )
        self.tags.add(tag)

    def remove_contexts(self, tags_text):
        for tag in ContextTag.objects.filter(tag__in=tags_text).all():
            self.tags.remove(tag)

    def is_complete(self):
        if self.a_it is not None:
            return True
        else:
            return False
    
    def get_local_datetime(self):
        return self.timezone.localize(self.time)

    @property
    def timezone(self):
        if hasattr(self, '_timezone'):
            return self._timezone
        service = DayService(user = self._user)
        tz = service.get_timezone_at(self.time)
        self._timezone = tz
        return self._timezone

    def fitbit_previous_step_count(self, duration):
        service = FitbitStepCountService(user = self.user)
        return service.get_step_count_between(
            start = self.time - timedelta(minutes=duration),
            end = self.time
        )

    def fitbit_post_step_count(self, duration):
        service = FitbitStepCountService(user = self.user)
        return service.get_step_count_between(
            start = self.time,
            end = self.time + timedelta(minutes=duration)
        )

    def watch_app_previous_step_count(self, duration):
        return 10

    def watch_app_post_step_count(self, duration):
        return 10

    def __str__(self):
        formatted_time = self.time.strftime("%Y-%m-%d at %H:%M")
        if self.a_it is None:
            return "On %s for %s (undecided)" % (formatted_time, self.user)
        else:
            return "On %s for %s (decided)" % (formatted_time, self.user)

class DecisionContext(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decision = models.ForeignKey(Decision)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
