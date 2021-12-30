import json
import uuid

from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User

from days.models import LocalizeTimezoneQuerySet
from participants.models import Study, Participant
from user_event_logs.models import EventLog
from .clients import OneSignalClient

class OneSignalInfo(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, null=True)
    app_id = models.CharField(max_length=255, null=False)
    app_key = models.CharField(max_length=255, null=False)
    
    def get(user=None, study=None):
        def get_default_key_id(user):
            EventLog.debug(user)
            if not hasattr(settings, 'ONESIGNAL_APP_ID'):
                EventLog.debug(user)
                raise ImproperlyConfigured('No OneSignal APP ID')
            EventLog.debug(user)
            app_id = settings.ONESIGNAL_APP_ID
            EventLog.debug(user, "default app_id: {}".format(app_id))
            if not hasattr(settings, 'ONESIGNAL_API_KEY'):
                EventLog.debug(user)
                raise ImproperlyConfigured('No OneSignal API KEY')
            EventLog.debug(user)
            app_key = settings.ONESIGNAL_API_KEY
            EventLog.debug(user, "default api_key: {}".format(app_key))
                
            return (app_id, app_key)
        EventLog.debug(user)
        if user is not None:
            EventLog.debug(user)
            study_query = Participant.objects.filter(user=user)
            EventLog.debug(user)
            if study_query.exists():
                EventLog.debug(user)
                study = study_query.first().cohort.study
                info_query = OneSignalInfo.objects.filter(study=study)
                EventLog.debug(user)
                if info_query.exists():
                    EventLog.debug(user)
                    one_signal_info = OneSignalInfo.objects.filter(study=study).first()
                    EventLog.debug(user)
                    return (one_signal_info.app_id, one_signal_info.app_key)
            EventLog.debug(user)
            return get_default_key_id(user)
                
        elif study is not None: 
            EventLog.debug(user)           
            query = OneSignalInfo.objects.filter(study=study)
            EventLog.debug(user)
            if query.exists():
                EventLog.debug(user)
                one_signal_info = OneSignalInfo.objects.filter(study=study).first()
                EventLog.debug(user)
                return (one_signal_info.app_id, one_signal_info.app_key)
            else:
                EventLog.debug(user)
                return get_default_key_id(user)
        else:
            EventLog.debug(user)
            return get_default_key_id(user)
            
            
class Device(models.Model):

    ANDROID = 'android'
    IOS = 'ios'
    ONESIGNAL = 'onesignal'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    token = models.CharField(max_length=255)
    type = models.CharField(max_length=10, null=True, blank=True)

    active = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s (%s)' % (self.type, self.token)

class MessageReceiptQuerySet(LocalizeTimezoneQuerySet):

    _receipts_loaded = False
    _localize_datetimes = False
    _datetime_localized = False

    def get_queryset(self):
        return super().get_queryset() \
        .prefetch_related('type')

    def _clone(self, *args, **kwargs):
        clone = super()._clone(*args, **kwargs)
        clone._localize_datetimes = self._localize_datetimes
        return clone

    def _fetch_all(self):
        super()._fetch_all()
        if self._result_cache and not self._receipts_loaded:
            self._fetch_message_receipts()
            self._receipts_loaded = True
        if self._result_cache and self._localize_datetimes and not self._datetime_localized:
            self.localize_messages(self._result_cache)
            self._datetime_localized = True

    def _fetch_message_receipts(self):
        if self._result_cache:
            message_receipts = {}
            message_receipt_query = MessageReceipt.objects.filter(
                message_id__in = [_message.id for _message in self._result_cache]
            )
            for _receipt in message_receipt_query.all():
                if _receipt.message_id not in message_receipts:
                    message_receipts[_receipt.message_id] = {}
                message_receipts[_receipt.message_id][_receipt.type] = _receipt.time
            for _message in self._result_cache:
                if _message.id in message_receipts:
                    _message._message_receipts = message_receipts[_message.id]
                else:
                    _message._message_receipts = {}

    def localize_datetimes(self):
        self._localize_datetimes = True
        return self

    def localize_messages(self, messages):
        user_ids = []
        start = None
        end = None
        for message in messages:
            if message.recipient_id not in user_ids:
                user_ids.append(message.recipient_id)
            if not start or message.created < start:
                start = message.created
            if not end or message.created > end:
                end = message.created        
        timezone_dict = self.cache_timezones(user_ids, start, end)
        for message in messages:
            message_receipts = message.get_message_receipts()
            for key, value in message_receipts.items():
                message_receipts[key] = self.set_timezone(timezone_dict, message.recipient_id, value)
            message.set_message_receipts(message_receipts)


# TODO: IMPORTANT -> ASK ABOUT EXPIRATION DATES ON NOTIFICATIONS
class Message(models.Model):

    DATA = 'data'
    NOTIFICATION = 'notification'
    MESSAGE_TYPES = [
        (DATA, 'Data'),
        (NOTIFICATION, 'Notification')
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)

    recipient = models.ForeignKey(User, on_delete = models.CASCADE)
    device = models.ForeignKey(Device, null=True, on_delete = models.CASCADE)

    data = models.JSONField(null=True)
    content = models.TextField(null=True)
    title = models.TextField(max_length=150, null=True)
    body = models.TextField(max_length=355, null=True)
    collapse_subject = models.CharField(max_length=150, null=True)

    external_id = models.CharField(max_length=150, null=True)

    created = models.DateTimeField(auto_now_add=True)

    objects = MessageReceiptQuerySet.as_manager()

    def __str__(self):
        return '%s (%s)' % (self.recipient.username, self.message_type)

    def __load_message_receipts(self):
        message_receipts = {}
        for _receipt in MessageReceipt.objects.filter(message=self):
            message_receipts[_receipt.type] = _receipt.time
        self._message_receipts = message_receipts

    def __get_receipt_time(self, receipt_type):
        message_receipts = self.get_message_receipts()
        if receipt_type in message_receipts:
            return self._message_receipts[receipt_type]
        else:
            return None

    def update_message_receipts(self):
        EventLog.info(self.recipient.username, "update_message_receipts() is called")
        if self.device.type != 'onesignal':
            EventLog.info(self.recipient.username, "self.device.type is not onesignal")
            raise RuntimeError('No client for message device')
        client = OneSignalClient(self.device)
        EventLog.info(self.recipient.username, "client is initialized")
        receipts = client.get_message_receipts(self.external_id)
        EventLog.info(self.recipient.username, "message receipts are fetched")
        for receipt_type, receipt_datetime in receipts.items():
            try:
                receipt = MessageReceipt.objects.get(
                    message = self,
                    type = receipt_type
                )
            except MessageReceipt.DoesNotExist:
                receipt = MessageReceipt(
                    message = self,
                    type = receipt_type
                )
            receipt.time = receipt_datetime
            receipt.save()

    def get_message_receipts(self):
        if not hasattr(self, '_message_receipts'):
            self.__load_message_receipts()
        return self._message_receipts

    def set_message_receipts(self, message_receipts):
        self._message_receipts = message_receipts

    @property
    def sent(self):
        return self.__get_receipt_time(MessageReceipt.SENT)

    @property
    def received(self):
        return self.__get_receipt_time(MessageReceipt.RECEIVED)

    @property
    def displayed(self):
        return self.__get_receipt_time(MessageReceipt.DISPLAYED)
    
    @property
    def opened(self):
        return self.__get_receipt_time(MessageReceipt.OPENED)

    @property
    def engaged(self):
        return self.__get_receipt_time(MessageReceipt.ENGAGED)

class MessageReceipt(models.Model):
    SENT = 'sent'
    RECEIVED = 'received'
    DISPLAYED = 'displayed'
    OPENED = 'opened'
    ENGAGED = 'engaged'


    MESSAGE_RECEIPT_TYPES = [SENT, RECEIVED, DISPLAYED, OPENED, ENGAGED]

    MESSAGE_RECEIPT_CHOICES = (
        (SENT, 'Sent'),
        (RECEIVED, 'Received'),
        (DISPLAYED, 'Displayed'),
        (OPENED, 'Opened'),
        (ENGAGED, 'Engaged')
    )

    message = models.ForeignKey(Message, on_delete = models.CASCADE)
    time = models.DateTimeField()
    type = models.CharField(max_length=20, choices=MESSAGE_RECEIPT_CHOICES)