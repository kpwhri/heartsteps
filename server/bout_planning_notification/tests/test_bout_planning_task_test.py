from django.test import TestCase
from bout_planning_notification.models import User, FirstBoutPlanningTime
from rest_framework.test import APITestCase
from django.urls import reverse
from bout_planning_notification.tasks import bout_planning_decision_making, BoutPlanningFlagException
from feature_flags.models import FeatureFlags
from bout_planning_notification.receivers import FirstBoutPlanningTime_updated
from locations.models import Place


class BoutPlanningTaskTest(TestCase):
    def setUp(self):
        """Create testing user"""
        self.user = User.objects.create(username="test")

    def tearDown(self):
        """Destroying testing user"""
        self.user.delete()

    def test_task_1(self):
        # bout_planning_decision_making() should be called with username
        self.assertRaises(TypeError, bout_planning_decision_making)
        # bout_planning_decision_making() should be called with a string
        self.assertRaises(AssertionError, bout_planning_decision_making, 1)

    def test_task_2(self):
        # if there's no feature flag for the user, BoutPlanningFlagException is raised
        self.assertRaises(BoutPlanningFlagException,
                          bout_planning_decision_making, self.user.username)

        # if there's a feature flag for the user, but it doesn't contain "bout_planning" feature flag, BoutPlanningFlagException is raised
        FeatureFlags.create(self.user)
        self.assertRaises(BoutPlanningFlagException,
                          bout_planning_decision_making, self.user.username)

        FeatureFlags.update(self.user, "bout_planning")
        bout_planning_decision_making(self.user.username)

    def test_FirstBoutPlanningTime_updated_1(self):
        user1 = User.objects.create(username="user1")

        Place.objects.create(
            user=user1,
            type=Place.HOME,
            address=
            '9500 Gilman Dr, La Jolla, California, United States of America',
            latitude=32.88239,
            longitude=-117.23498)

        obj1 = FirstBoutPlanningTime(user=user1, hour=7, minute=0)
        obj1.save()
        