from django.db import models
from django.contrib.auth.models import User


# class GoodMorningMessage(models.Model):
#     """
#     Represents a good morning intervention message
#     """
#     user = models.ForeignKey(User)
#     server_sent_dtm = models.DateTimeField()
#     server_created_dtm = models.DateTimeField()
#     send_motivation_message = models.BooleanField()
#     # Or maybe IntegerField()?
#     #motivation_message_list_id = models.ForeignKey(MotivationMessageList)
#     send_suggested_step_count = models.BooleanField()
#     suggested_step_count = models.IntegerField()
#     weather_temperature = models.IntegerField()
#     # Where are we getting this from?
#     # Should this tie out to a record in WeatherHistory table instead?
#     weather_city_state = models.TextField()
#     # When the app received the message
#     app_received_dtm = models.DateTimeField()
#     app_received_tz = models.DateTimeField()
#     app_received_offset = models.IntegerField()
#     # When the user began interaction with the message
#     app_start_dtm = models.DateTimeField()
#     app_start_tz = models.DateTimeField()
#     app_start_offset = models.IntegerField()
#     # When the user responded to the message
#     app_respond_dtm = models.DateTimeField()
#     app_respond_tz = models.DateTimeField()
#     app_respond_offset = models.IntegerField()
#     # Initial specs include both below. Necessary?  Possible?
#     user_responded = models.BooleanField()
#     user_responded_step_count = models.BooleanField()


class Participant(models.Model):
    """
    Represents a study participant
    """
    user = models.ForeignKey(User)
#    heartsteps_id = models.CharField(max_length=10)
    # Unique device ID as Fitbit stores it
    tracker_id = models.CharField(max_length=24)
    enrollment_token = models.CharField(max_length=10)
#    access_token = models.CharField(max_length=10)
#    firebase_token = models.CharField(max_length=10)
#    preferred_timezone = models.CharField(max_length=5)
#    do_not_disturb = models.BooleanField(default=True)
#    server_created_dtm = models.DateTimeField()


# class UserHealthData(models.Model):
#     """
#     Represents a piece of user-tracked health data
#     Probably limited to blood_glucose, blood_pressure, weight
#     """
#     UHD_TYPE_CHOICES = (
#         (1, 'Blood Glucose'),
#         (2, 'Blood Pressure'),
#         (3, 'Weight')
#     )
#     participant = models.ForeignKey(Participant)
#     uhd_type = models.IntegerField(choices=UHD_TYPE_CHOICES)
#     value = models.CharField(max_length=20)
#     unit = models.CharField(max_length=10)
#     app_sent_dtm = models.DateTimeField()
#     app_sent_tz = models.DateTimeField()
#     app_sent_offset = models.IntegerField()
#     server_created_dtm = models.DateTimeField()


# class WeatherForecast(models.Model):
#     """
#     Represents an hourly weather forecast from our weather API
#     """
#     weather_id = models.TextField()
#     latitude = models.FloatField()
#     longitude = models.FloatField()
#     time = models.DateTimeField()
#     precip_probability = models.FloatField()
#     precip_type = models.TextField()
#     temperature = models.FloatField()
#     apparent_temperature = models.FloatField()
#     wind_speed = models.FloatField()
#     cloud_cover = models.FloatField()
#     server_created_dtm = models.DateTimeField()
