import requests, json, math
from datetime import timedelta
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
        if not hasattr(settings, 'ANTI_SEDENTARY_DECISION_MINUTE_INTERVAL'):
            raise AntiSedentaryClient.NoConfiguration('No anti-sedentary minute interval')
        self.minute_interval = settings.ANTI_SEDENTARY_DECISION_MINUTE_INTERVAL
        self.service_url = settings.ANTI_SEDENTARY_SERVICE_URL

    def make_request(self, uri, data):
        url = urljoin(self.service_url, uri)
        data['userid'] = str(self.__user.username)
        request_record = ServiceRequest(
            user = self.__user,
            url = url,
            name = 'AntiSedentaryService: %s' % (uri),
            request_data = json.dumps(data),
            request_time = timezone.now()
        )
        try:
            response = requests.post(url, json=data)
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

    def format_decision_datetime(self, time):
        rounded_minutes = math.ceil(time.minute/self.minute_interval)*self.minute_interval
        difference = timedelta(minutes=rounded_minutes) - timedelta(minutes=time.minute)
        rounded_time = time + difference
        return self.format_datetime(rounded_time)

    def format_datetime(self, time):
        return time.strftime('%Y-%m-%d %H:%M')

    def format_boolean(self, bool):
        if bool:
            return 1
        else:
            return 0

    def decide(self, decision, step_count, time, day_start, day_end):
        data = {
            'decisionid': str(decision.id),
            'time': self.format_decision_datetime(time),
            'daystart': self.format_datetime(day_start),
            'dayend': self.format_datetime(day_end),
            'state': self.format_boolean(decision.sedentary),
            'available': self.format_boolean(decision.available),
            'steps': step_count
        }
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

    
    def update(self, decisions, day_start, day_end):
        for decision in decisions:
            try:
                response = self.make_request(
                    uri = 'nightly',
                    data = {
                        'daystart': self.format_datetime(day_start),
                        'dayend': self.format_datetime(day_end),
                        'decisionid': decision['id'],
                        'time': self.format_decision_datetime(decision['time']),
                        'state': self.format_boolean(decision['sedentary']),
                        'steps': decision['steps']
                    }
                )
            except AntiSedentaryClient.RequestError:
                pass

