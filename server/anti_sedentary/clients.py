import requests, json
from urllib.parse import urljoin

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from service_requests.models import ServiceRequest

from .models import User

class AntiSedentaryClient:

    class NoConfiguration(ImproperlyConfigured):
        pass
    
    class RequestError(RuntimeError):
        pass

    def __init__(self, user=None, username=None):
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass
        if not user:
            raise AntiSedentaryClient.NoConfiguration('No user')
        self.__user = user

        if not hasattr(settings, 'ANTI_SEDENTARY_SERVICE_URL'):
            raise AntiSedentaryClient.NoConfiguration('No anti-sedentary service url')
        self.service_url = settings.ANTI_SEDENTARY_SERVICE_URL

    def make_request(self, uri, data):
        url = urljoin(self.service_url, uri)
        data['userid'] = str(self.__user.id)
        request_record = ServiceRequest(
            user = self.__user,
            url = url,
            request_data = json.dumps(data),
            request_time = timezone.now()
        )
        try:
            response = requests.post(url, json)
        except:
            request_record.save()
            raise RequestError('Error making request')
        request_record.response_code = response.status_code
        request_record.response_data = response.text
        request_record.response_time = timezone.now()
        request_record.save()

        try:
            return json.loads(response.text)
        except:
            return response.text

    def __format_datetime(self, time):
        return time.strftime('%Y-%m-%d %H:%M')

    def decide(self, decision, step_count, day_start, day_end):
        data = {
            'decisionid': str(decision.id),
            'time': self.__format_datetime(decision.time),
            'daystart': self.__format_datetime(day_start),
            'dayend': self.__format_datetime(day_end),
            'state': 0,
            'available': 0,
            'steps': step_count
        }
        if decision.sedentary:
            data['state'] = 1
        if decision.available:
            data['available'] = 1
        try:
            response = self.make_request(
                uri = 'decision',
                data = data
            )
        except AntiSedentaryClient.RequestError:
            decision.treated = False
            decision.treatment_probability = 0
            decision.available = False
            decision.unavailable_reason = 'Anti-sedentary service request failed'
            decision.save()
            return decision.treated
        if response['a_it'] is 1:
            decision.treated = True
        else:
            decision.treated = False
        decision.treatment_probability = response['pi_it']
        decision.save()
        
        return decision.treated

    
    def update(self, data):
        pass
