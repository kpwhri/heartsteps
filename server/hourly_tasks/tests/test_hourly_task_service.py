import pytz
from unittest.mock import patch

from django.test import override_settings
from django_celery_beat.models import PeriodicTask, PeriodicTasks

from days.services import DayService
from days.signals import timezone_updated

from heartsteps.tests import HeartStepsTestCase
from daily_tasks.models import User, DailyTask
from hourly_tasks.models import HourlyTask

from nlm.services import LogService

class HourlyTaskUpdateTest(HeartStepsTestCase):

    def setUp(self):
        super().setUp()
        # timezone_patch = patch.object(DayService, 'get_current_timezone')
        # self.addCleanup(timezone_patch.stop)
        # self.timezone = timezone_patch.start()
        # self.timezone.return_value = pytz.timezone('Etc/GMT+7')
        
    def tearDown(self):
        super().tearDown()
        


    def create_task(self, minute=0, arguments={}):
        return HourlyTask.create_hourly_task(
            user = self.user,
            category = 'example',
            task = 'hourly_tasks.tests.HourlyTaskTestingTask.run',
            name = 'Name of task!',
            arguments = arguments,
            minute = minute
        )

    


    def test_create_hourly_tasks(self):
        newHourlyTask = self.create_task(
            minute = 0
        )

        
        # print("newDailyTask.__dict__={}".format(newHourlyTask.__dict__))
        

        # print("newDailyTask.task.__dict__={}".format(newHourlyTask.task.__dict__))
        # print("newDailyTask.task.crontab.__dict__={}".format(newHourlyTask.task.crontab.__dict__))
        
    #     # hour was set to 2, timezone is +7 == 9 GMT
    #     self.assertEqual(task.crontab.hour, '9')
    #     self.assertEqual(task.crontab.minute, '0')

    #     self.timezone.return_value = pytz.timezone('Etc/GMT+4')
    #     timezone_updated.send(User, username="test")

    #     task = PeriodicTask.objects.get()
    #     # hour was set to 2, timezone is +4
    #     self.assertEqual(task.crontab.hour, '6')
    #     self.assertEqual(task.crontab.minute, '0')

    # def test_registers_tasks_for_specific_day(self):
    #     self.timezone.return_value = pytz.timezone('Etc/GMT-8')
    #     self.create_task(
    #         minute = 30,
    #         hour = 20,
    #         day = 'friday'
    #     )

    #     task = PeriodicTask.objects.get()
    #     self.assertEqual(task.crontab.day_of_week, '5')

    # def test_regiesters_correct_day_with_timezone_change(self):
    #     self.timezone.return_value = pytz.timezone('UTC')
    #     self.create_task(
    #         hour = 6,
    #         day = 'sunday'
    #     )

    #     task = PeriodicTask.objects.get()
    #     self.assertEqual(task.crontab.day_of_week, '0')
    #     self.assertEqual(task.crontab.hour, '6')

    #     self.timezone.return_value = pytz.timezone('Etc/GMT-8')
    #     timezone_updated.send(User, username="test")

    #     task = PeriodicTask.objects.get()
    #     self.assertEqual(task.crontab.day_of_week, '6')
    #     self.assertEqual(task.crontab.hour, '22')
