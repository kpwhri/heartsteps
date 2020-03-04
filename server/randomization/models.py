import uuid, random
from datetime import datetime
from datetime import timedelta
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User

from behavioral_messages.models import MessageTemplate
from days.services import DayService
from fitbit_activities.services import FitbitStepCountService
from locations.models import Location
from locations.models import Place
from locations.services import LocationService
from push_messages.models import Message
from push_messages.services import PushMessageService
from watch_app.services import StepCountService as WatchAppStepCountService
from weather.models import WeatherForecast

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
    RECENTLY_ACTIVE = 'recently-active'
    ON_VACATION = 'on-vacation'
    NO_STEP_COUNT_DATA = 'no-step-count-data'
    DISABLED = 'disabled'
    SERVICE_ERROR = 'service-error'

    CHOICES = [
        (UNREACHABLE, 'Unreachable'),
        (NOTIFICATION_RECENTLY_SENT, 'Notification recently sent'),
        (NOT_SEDENTARY, 'Not sedentary'),
        (NO_STEP_COUNT_DATA, 'No step-count data'),
        (ON_VACATION, 'On vacation'),
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
    SEDENTARY_STEP_COUNT = 150
    SEDENTARY_DURATION_MINUTES = 40

    UNAVAILABLE_UNREACHABLE = UnavailableReason.UNREACHABLE
    UNAVAILABLE_NOTIFICATION_RECENTLY_SENT = UnavailableReason.NOTIFICATION_RECENTLY_SENT
    UNAVAILABLE_NOT_SEDENTARY = UnavailableReason.NOT_SEDENTARY
    UNAVAILABLE_RECENTLY_ACTIVE = UnavailableReason.RECENTLY_ACTIVE
    UNAVAILABLE_ON_VACATION = UnavailableReason.ON_VACATION
    UNAVAILABLE_NO_STEP_COUNT_DATA = UnavailableReason.NO_STEP_COUNT_DATA
    UNAVAILABLE_DISABLED = UnavailableReason.DISABLED
    UNAVAILABLE_SERVICE_ERROR = UnavailableReason.SERVICE_ERROR

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        related_name = '+',
        on_delete = models.CASCADE
    )

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

    def make_unavailable_property(property_reason):
        def get_reason(self):
            try:
                UnavailableReason.objects.get(
                    decision = self,
                    reason = property_reason
                )
                return True
            except UnavailableReason.DoesNotExist:
                return False
        return property(get_reason)
    
    def is_available(self):
        reasons = UnavailableReason.objects.filter(
            decision = self
        ).count()
        if reasons > 0:
            return False
        else:
            return True

    def add_unavailable_reason(self, reason):
        UnavailableReason.objects.create(
            decision = self,
            reason = reason
        )

    def update(self):
        UnavailableReason.objects.filter(decision=self).delete()
        if self.imputed:
            self.add_unavailable_reason(UnavailableReason.UNREACHABLE)
        if self.is_notification_recently_sent():
            self.add_unavailable_reason(UnavailableReason.NOTIFICATION_RECENTLY_SENT)
        try:
            if not self._is_sedentary():
                self.add_unavailable_reason(UnavailableReason.NOT_SEDENTARY)
                self.sedentary = False
            else:
                self.sedentary = True
        except WatchAppStepCountService.NoStepCountRecorded:
            self.handle_no_step_count()
        if self.is_recently_active():
            self.add_unavailable_reason(UnavailableReason.RECENTLY_ACTIVE)
        self.available = self.is_available()
        self.save()
    
    def handle_no_step_count(self):
        self.add_unavailable_reason(UnavailableReason.NO_STEP_COUNT_DATA)
        self.sedentary = False

    def is_notification_recently_sent(self):
        return self.__is_message_recently_sent()

    def __is_message_recently_sent(self, message_model=None, duration_minutes=60):
        if not message_model:
            message_model = Message
        recent_notification_count = message_model.objects.filter(
            recipient = self.user,
            created__range = [
                self.time - timedelta(minutes = duration_minutes),
                self.time
            ],
            message_type = Message.NOTIFICATION
        ).count()
        if recent_notification_count > 0:
            return True
        else:
            return False

    def _get_sedentary_step_count(self):
        service = WatchAppStepCountService(user = self.user)
        return service.get_step_count_between(
            start = self.time - timedelta(minutes = self.get_sedentary_duration_minutes()),
            end = self.time
        )

    def get_sedentary_duration_minutes(self):
        return self.SEDENTARY_DURATION_MINUTES

    @property
    def sedentary_step_count(self):
        return self.SEDENTARY_STEP_COUNT

    def _is_sedentary(self):
        steps = self._get_sedentary_step_count()
        if steps < self.sedentary_step_count:
            return True
        else:
            return False

    def get_sedentary_step_count(self):
        try:
            return self._get_sedentary_step_count()
        except WatchAppStepCountService.NoStepCountRecorded:
            return 0
        
    def is_sedentary(self):
        try:
            return self._is_sedentary()
        except WatchAppStepCountService.NoStepCountRecorded:
            return False

    def _get_recently_active_minutes(self):
        if hasattr(settings, 'RANDOMIZATION_RECENTLY_ACTIVE_DURATION_MINUTES'):
            return settings.RANDOMIZATION_RECENTLY_ACTIVE_DURATION_MINUTES
        return 120

    def _get_recently_active_step_count_threshold(self):
        if hasattr(settings, 'RANDOMIZATION_RECENTLY_ACTIVE_STEP_COUNT_THRESHOLD'):
            return settings.RANDOMIZATION_RECENTLY_ACTIVE_STEP_COUNT_THRESHOLD
        return 2000

    def is_recently_active(self):
        try:
            service = WatchAppStepCountService(user = self.user)
            step_count = service.get_step_count_between(
                start = self.time - timedelta(minutes = self._get_recently_active_minutes()),
                end = self.time
            )
            if step_count > self._get_recently_active_step_count_threshold():
                return True
            else:
                return False
        except WatchAppStepCountService.NoStepCountRecorded:
            return False

    unavailable_no_step_count_data = make_unavailable_property(UnavailableReason.NO_STEP_COUNT_DATA)
    unavailable_not_sedentary = make_unavailable_property(UnavailableReason.NOT_SEDENTARY)
    unavailable_recently_active = make_unavailable_property(UnavailableReason.RECENTLY_ACTIVE)
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
        return self.time.astimezone(self.timezone)

    @property
    def timezone(self):
        if hasattr(self, '_timezone'):
            return self._timezone
        service = DayService(user = self.user)
        tz = service.get_timezone_at(self.time)
        self._timezone = tz
        return self._timezone
    
    def get_location(self):
        if hasattr(self, '_location'):
            return self._location
        location_content_type = ContentType.objects.get_for_model(Location)
        existing_decision_locations = DecisionContext.objects.filter(
            decision = self,
            content_type = location_content_type
        ).all()
        if len(existing_decision_locations) > 0:
            self._location = existing_decision_locations[0].content_object
            return self._location
        else:
            return None

    def update_location(self):
        location_content_type = ContentType.objects.get_for_model(Location)
        existing_decision_locations = DecisionContext.objects.filter(
            decision = self.decision,
            content_type = location_content_type
        ).delete()

        try:
            location_service = LocationService(self.user)
            location = location_service.get_location_on(self.time)
            DecisionContext.objects.create(
                decision = self.decision,
                content_object = location
            )
            self.location = location
            return location
        except LocationService.UnknownLocation:
            return None

    def get_location_type(self):
        location = self.get_location()
        if location:
            location_service = LocationService(self.user)
            return location_service.categorize_location(
                latitude = location.latitude,
                longitude = location.longitude
            )
        else:
            return Place.OTHER

    def get_forecast(self):
        if hasattr(self, '_forecast'):
            return self._forecast
        else:
            forecast_content_type = ContentType.objects.get_for_model(WeatherForecast)
            context = DecisionContext.objects.filter(
                decision = self,
                content_type = forecast_content_type
            ).last()
            if context:
                self._forecast = context.content_object
                return self._forecast
        return None

    @property
    def precipitation_type(self):
        forecast = self.get_forecast()
        if forecast:
            return forecast.precip_type
        else:
            return None

    @property
    def precipitation_probability(self):
        forecast = self.get_forecast()
        if forecast:
            return forecast.precip_probability
        else:
            return None 

    @property
    def temperature(self):
        forecast = self.get_forecast()
        if forecast:
            return forecast.temperature
        else:
            return None

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

class DecisionRating(models.Model):
    decision = models.OneToOneField(
        Decision,
        on_delete = models.CASCADE,
        related_name = 'rating'
    )
    liked = models.NullBooleanField()
    comments = models.CharField(
        max_length=250,
        null = True
    )
