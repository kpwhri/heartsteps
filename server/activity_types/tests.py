from django.test import TestCase

from .models import ActivityType

class ActivityTypeTests(TestCase):

    def test_remove_spaces_from_name(self):
        ActivityType.objects.create(
            name = "activity with spaces",
            title= "Activity, with spaces"
        )

        activity_type = ActivityType.objects.get()
        self.assertEqual(activity_type.name, 'activity_with_spaces')
        self.assertEqual(activity_type.title, 'Activity, with spaces')
