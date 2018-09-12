from django.test import TestCase

# class ActivityPlansListTest(APITestCase):

#     def test_create_activity_log(self):
#         user = User.objects.create(username="test")
#         ActivityType.objects.create(
#             name="swim"
#         )

#         self.client.force_authenticate(user=user)
#         response = self.client.post(reverse('activity-logs'), {
#             'type': 'swim',
#             'start': '2018-09-05T14:45',
#             'duration': '30',
#             'vigorous': True,
#             'enjoyed': 5
#         })

#         self.assertEqual(response.status_code, 201)
