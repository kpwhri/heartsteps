from datetime import date
from unittest.mock import patch

from django.test import TestCase

from participants.models import User
from participants.signals import nightly_update

from .tasks import export_user_data

class QueuesDataDownload(TestCase):

    @patch.object(export_user_data, 'apply_async')
    def test_nightly_update_queues_data_download(self, export_user_data):
        user = User.objects.create(username='test')

        nightly_update.send(
            sender=User,
            user=user,
            day=date.today()
        )

        export_user_data.assert_called_with(kwargs={
            'username': 'test'
        })


