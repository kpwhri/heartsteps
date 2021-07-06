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
from locations.models import Location
from locations.services import LocationService
from push_messages.models import Message
from fitbit_clock_face.services import StepCountService as WatchAppStepCountService
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

class DecisionContextQuerySet(models.QuerySet):

    _load_notification = False
    _load_notification_done = False

    _load_unavailable_reasons = False
    _load_unavailable_reasons_done = False

    _load_location = False
    _load_location_done = False

    _load_weather_forecast = False
    _load_weather_forecast_done = False

    _load_message_template = False
    _load_message_template_done = False
    _message_template_model = None

    _load_rating = False
    _load_rating_done = False

    def prefetch_rating(self):
        self._load_rating = True
        return self

    def prefetch_weather_forecast(self):
        self._load_weather_forecast = True
        return self

    def prefetch_notification(self):
        self._load_notification = True
        return self

    def prefetch_message_template(self, message_template_model):
        self._load_message_template = True
        self._message_template_model = message_template_model
        return self

    def prefetch_unavailable_reasons(self):
        self._load_unavailable_reasons = True
        return self

    def prefetch_location(self):
        self._load_location = True
        return self
    
    def _fetch_all(self):
        now = datetime.now()
        super()._fetch_all()
        if self._load_notification and not self._load_notification_done and self._result_cache:
            self._fetch_notification()
            self._load_notification_done = True
        if self._load_unavailable_reasons and not self._load_unavailable_reasons_done and self._result_cache:
            self._fetch_unavailable_reasons()
            self._load_unavailable_reasons_done = True
        if self._load_location and not self._load_location_done and self._result_cache:
            self._fetch_fresh_locations()
            self._load_location_done = True
        if self._load_weather_forecast and not self._load_weather_forecast_done and self._result_cache:
            self._fetch_weather_forecast()
            self._load_weather_forecast_done = True
        if self._load_message_template and not self._load_message_template_done and self._result_cache:
            self._fetch_message_template()
            self._load_message_template_done = True
        if self._load_rating and not self._load_rating_done and self._result_cache:
            self._fetch_rating()
            self._load_rating_done = True
        diff = datetime.now() - now

    def _clone(self, **kwargs):
        clone = super()._clone(**kwargs)
        clone._load_notification = self._load_notification
        clone._load_unavailable_reasons = self._load_unavailable_reasons
        clone._load_location = self._load_location
        clone._load_weather_forecast = self._load_weather_forecast
        clone._load_message_template = self._load_message_template
        clone._message_template_model = self._message_template_model
        clone._load_rating = self._load_rating
        return clone

    def _get_context_objects(self, model):
        message_template_content_type = ContentType.objects.get_for_model(model)
        decision_ids = [_decision.id for _decision in self._result_cache]
        return DecisionContext.objects.filter(
            decision_id__in = decision_ids,
            content_type = message_template_content_type
        ).all()        

    def _fetch_rating(self):
        decision_ids = [_decision.id for _decision in self._result_cache]
        rating_query = DecisionRating.objects.filter(
            decision_id__in = decision_ids
        )
        rating_by_decision_id = {}
        for rating in rating_query.all():
            rating_by_decision_id[rating.decision_id] = rating
        for _decision in self._result_cache:
            if _decision.id in rating_by_decision_id:
                _decision._rating = rating_by_decision_id[_decision.id]
            else:
                _decision._rating = None

    def _fetch_message_template(self):
        if self._message_template_model:
            message_template_model = self._message_template_model
        else:
            message_template_model = MessageTemplate
        context_objects = self._get_context_objects(message_template_model)
        obj_id_to_decision_id = {}
        for _context in context_objects:
            obj_id_to_decision_id[_context.object_id] = str(_context.decision_id)
        message_templates = message_template_model.objects.filter(
            id__in = obj_id_to_decision_id.keys()
        ).all()
        message_template_by_decision_id = {}
        for _mt in message_templates:
            decision_id = obj_id_to_decision_id[_mt.id]
            message_template_by_decision_id[decision_id] = _mt

        for _decision in self._result_cache:
            if str(_decision.id) in message_template_by_decision_id:
                _decision._message_template = message_template_by_decision_id[str(_decision.id)]
            else:
                _decision._message_template = None

    def _fetch_weather_forecast(self):
        weather_forecast_content_type = ContentType.objects.get_for_model(WeatherForecast)
        decision_ids = [_decision.id for _decision in self._result_cache]
        context_objects = DecisionContext.objects.filter(
            decision_id__in = decision_ids,
            content_type = weather_forecast_content_type
        ).all()
        weather_forecast_id_to_decision_id = {}
        for _context in context_objects:
            weather_forecast_id_to_decision_id[_context.object_id] = str(_context.decision_id)
        weather_forecasts = WeatherForecast.objects.filter(
            id__in = weather_forecast_id_to_decision_id.keys()
        ).all()
        weather_forecast_by_decision_id = {}
        for _forecast in weather_forecasts:
            decision_id = weather_forecast_id_to_decision_id[_forecast.id]
            weather_forecast_by_decision_id[decision_id] = _forecast

        for _decision in self._result_cache:
            decision_id = str(_decision.id)
            if decision_id in weather_forecast_by_decision_id:
                _decision._forecast = weather_forecast_by_decision_id[decision_id]
            else:
                _decision._forecast = None

    def _fetch_location(self):
        location_content_type = ContentType.objects.get_for_model(Location)
        decision_ids = [_decision.id for _decision in self._result_cache]
        context_objects = DecisionContext.objects.filter(
            decision_id__in = decision_ids,
            content_type = location_content_type
        ).all()
        location_id_to_decision_id = {}
        for _context in context_objects:
            location_id_to_decision_id[_context.object_id] = str(_context.decision_id)
        locations = Location.objects.filter(
            id__in = location_id_to_decision_id.keys()
        ).all()
        locations_by_decision_id = {}

        for _location in locations:
            decision_id = location_id_to_decision_id[_location.id]
            locations_by_decision_id[decision_id] = _location
        for _decision in self._result_cache:
            decision_id = str(_decision.id)
            if decision_id in locations_by_decision_id:
                _decision._location = locations_by_decision_id[decision_id]
            else:
                _decision._location = None
    
    def _fetch_fresh_locations(self):
        earliest_decision_time = None
        latest_decision_time = None
        user_ids = []
        for _decision in self._result_cache:
            if not earliest_decision_time or _decision.time < earliest_decision_time:
                earliest_decision_time = _decision.time
            if not latest_decision_time or _decision.time > latest_decision_time:
                latest_decision_time = _decision.time
            if _decision.user_id not in user_ids:
                user_ids.append(_decision.user_id)
        locations = Location.objects.filter(
            user_id__in = user_ids,
            time__gte = earliest_decision_time,
            time__lte = latest_decision_time
        ).order_by('time').all()
        locations = list(locations)
        locations_by_user_id = {}
        for _location in locations:
            if _location.user_id not in locations_by_user_id:
                locations_by_user_id[_location.user_id] = []
            locations_by_user_id[_location.user_id].append(_location)
        for _decision in sorted(self._result_cache, key=lambda x: x.time):
            locations = []
            if _decision.user_id in locations_by_user_id:
                locations = locations_by_user_id[_decision.user_id]
            decision_location = None
            while locations:
                _location = locations[0]
                if _location.time > _decision.time:
                    break
                _diff = _decision.time - _location.time
                if _diff.seconds > 60*60:
                    locations.pop(0)
                    continue
                if len(locations) > 1:
                    next_location = locations[1]
                    if next_location.time > _location.time and next_location.time <= _decision.time:
                        locations.pop(0)
                        continue
                decision_location = _location
                break
            _decision._location = decision_location

    def _fetch_notification(self):
        message_content_type = ContentType.objects.get_for_model(Message)
        decision_ids = [_decision.id for _decision in self._result_cache]
        context_objects = DecisionContext.objects.filter(
            decision_id__in = decision_ids,
            content_type = message_content_type
        ).all()

        message_id_to_decision_id = {}
        for _context in context_objects:
            message_id_to_decision_id[_context.object_id] = str(_context.decision_id)
        messages = Message.objects.filter(
            id__in = message_id_to_decision_id.keys()
        ).all()

        notifications_by_decision_id = {}
        for message in messages:
            if message.message_type == Message.NOTIFICATION:
                decision_id = message_id_to_decision_id[message.id]
                notifications_by_decision_id[decision_id] = message

        for _decision in self._result_cache:
            if str(_decision.id) in notifications_by_decision_id:
                _decision._notification = notifications_by_decision_id[str(_decision.id)]
            else:
                _decision._notification = None
    
    def _fetch_unavailable_reasons(self):
        decision_ids = [_decision.id for _decision in self._result_cache]
        unavailable_reasons = {}
        for _id in decision_ids:
            unavailable_reasons[_id] = []
        unavailable_reason_query = UnavailableReason.objects.filter(decision_id__in=decision_ids)
        for _reason in unavailable_reason_query.all():
            unavailable_reasons[_reason.decision_id].append(_reason.reason)
        for _decision in self._result_cache:
            _decision._unavailable_reasons = unavailable_reasons[_decision.id]

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
    available = models.BooleanField(null=True)
    sedentary = models.BooleanField(null=True)

    time = models.DateTimeField()

    treated = models.BooleanField(null=True, blank=True)
    treatment_probability = models.FloatField(null=True, blank=True)

    tags = models.ManyToManyField(ContextTag)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-time']

    @property
    def unavailable_reasons(self):
        if not hasattr(self,'_unavailable_reasons'):
            unavailable_reasons = UnavailableReason.objects.filter(
                decision = self
            ).all()
            self._unavailable_reasons = [_unavailable_reason.reason for _unavailable_reason in unavailable_reasons]
        return self._unavailable_reasons

    def make_unavailable_property(property_reason):
        def get_reason(self):
            if property_reason in self.unavailable_reasons:
                return True
            else:
                return False
        return property(get_reason)
    
    def is_available(self):
        if len(self.unavailable_reasons) > 0:
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

    def __is_message_recently_sent(self, duration_minutes=60):
        recent_notification_count = Message.objects.filter(
            recipient = self.user,
            collapse_subject = 'activity-suggestion',
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
        if hasattr(self, '_message_template'):
            return self._message_template
        else:
            try:
                context_object = DecisionContext.objects.get(
                    decision = self,
                    content_type = ContentType.objects.get_for_model(self.MESSAGE_TEMPLATE_MODEL)
                )
                message_template = context_object.content_object
                self._message_template = message_template
            except DecisionContext.DoesNotExist:
                self._message_template = None
            return self._message_template

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
        else:
            self._location = None
        return self._location

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
            return location.category
        else:
            return None

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
            else:
                self._forecast = None
            return self._forecast

    @property
    def rating(self):
        if not hasattr(self, '_rating'):
            try:
                rating = DecisionRating.objects.get(
                    decision = self
                )
                self._rating = rating
            except DecisionRating.DoesNotExist:
                self._rating = None
        return self._rating

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
    decision = models.ForeignKey(Decision, on_delete = models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete = models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

class DecisionRating(models.Model):
    decision = models.OneToOneField(
        Decision,
        on_delete = models.CASCADE,
        related_name = '+'
    )
    liked = models.BooleanField(null=True)
    comments = models.CharField(
        max_length=250,
        null = True
    )
