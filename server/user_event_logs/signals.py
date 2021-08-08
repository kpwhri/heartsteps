# from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
# from django.dispatch import receiver
# from django.core.signals import request_finished
# from django.db.models.signals import pre_save, post_save
#
# from .models import AuditEntry, EventLog
# from daily_step_goals.models import StepGoal
# from activity_summaries.models import Day
# from fitbit_api.models import FitbitSubscriptionUpdate, FitbitDeviceUpdate
# from watch_app.models import StepCount
# from hourly_tasks.models import HourlyTask
# from sms_messages.models import Message
#
# # The following signal receiver signals when the user logs in
# @receiver(user_logged_in)
# def log_user_login(sender, request, user, **kwargs):
#     print('user {} logged in through page {}'.format(user.username, request.META.get('HTTP_REFERER')))
#
# # The following signal receiver signals when the user log in fails
# @receiver(user_login_failed)
# def log_user_login_failed(sender, credentials, request, **kwargs):
#     print('user {} logged in failed through page {}'.format(credentials.get('username'), request.META.get('HTTP_REFERER')))
#
# # The following signal receiver signals when the user logs out
# @receiver(user_logged_out)
# def log_user_logout(sender, request, user, **kwargs):
#     print('user {} logged out through page {}'.format(user.username, request.META.get('HTTP_REFERER')))
#
# # The following signal receiver signals when a new step goal is created in the database
# @receiver(post_save, sender=StepGoal)
# def step_goal_handler(sender, **kwargs):
#     EventLog.objects.create(action='NEW STEP GOAL CREATED', status='SCS')
#     print("New daily step goal saved")
#
# # The following signal receiver signals when a new Day is created in the database
# @receiver(post_save, sender=Day)
# def day_handler(sender, **kwargs):
#     EventLog.objects.create(action='NEW DAY CREATED', status='SCS')
#     print("New day created")
#
# # FITBIT UPDATE USER LOGGING
#
# # Fitbit Subscription Update
# @receiver(post_save, sender=FitbitSubscriptionUpdate)
# def fitbit_subscription_handler(sender, **kwargs):
#     EventLog.objects.create(action='FITBIT SUBSCRIPTION UPDATED', status='SCS')
#     print("Fitbit subscription updated")
#
# # Fitbit Device Update
# @receiver(post_save, sender=FitbitDeviceUpdate)
# def fitbit_subscription_handler(sender, **kwargs):
#     EventLog.objects.create(action='FITBIT DEVICE UPDATED', status='SCS')
#     print("Fitbit device updated")
#
# # Fitbit watch app update
# @receiver(post_save, sender=StepCount)
# def fitbit_subscription_handler(sender, **kwargs):
#     EventLog.objects.create(action='WATCH APP STEP COUNT UPDATED', status='SCS')
#     print("Watch app steps updated")
#
# # HOURLY TASK USER LOGGING
# @receiver(post_save, sender=HourlyTask)
# def fitbit_subscription_handler(sender, **kwargs):
#     EventLog.objects.create(action='HOURLY TASK UPDATED', status='SCS')
#     print("Hourly task updated")
#
# # SMS MESSAGE USER LOGGING
# @receiver(post_save, sender=Message)
# def fitbit_subscription_handler(sender, **kwargs):
#     EventLog.objects.create(action='SMS MESSAGE SENT', status='SCS')
#     print("SMS Message sent")
#
# # TEST SIGNALS
# # The following signal receiver signals when a new audit entry is saved
# @receiver(post_save, sender=AuditEntry)
# def my_audit_handler(sender, **kwargs):
#     print("New audit entry saved")
#
# # The following signal receiver signals for ANY new request
# @receiver(request_finished)
# def my_callback(sender, **kwargs):
#     return None
