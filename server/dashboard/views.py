from django.conf import settings
from django.contrib.auth.models import User
# from django.shortcuts import render
from django.views.generic import ListView

from contact.models import ContactInformation
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_api.models import FitbitAccount, FitbitAccountUser
from participants.models import Participant
from sms_service.forms import SendSMSForm
from sms_service.views import SendSmsCreateView


class DashboardListView(ListView):
    model = Participant
    queryset = Participant.objects.all().prefetch_related('user').order_by('heartsteps_id')
    template_name = 'dashboard/index.html'

    # Add the Twilio from-number for the form
    def get_context_data(self, **kwargs):
        context = super(DashboardListView, self).get_context_data(**kwargs)
        context['from_number'] = settings.TWILIO_PHONE_NUMBER
        context['form'] = SendSMSForm
        return context

    def post(self, request, *args, **kwargs):
        return SendSmsCreateView.as_view()(request)

# def index(request):
#     participant_list = Participant.objects.all().prefetch_related('user').order_by('heartsteps_id')
#     context = {'participant_list': participant_list}

#     print(request.method)

#     # n = 0
#     # for p in participant_list:
#     #     n += 1
#     #     print("Participant #" + str(n))
#     #     u = p.user
#     #     if u:
#     #         print("User ID: " + str(u.id))

#     #         try:
#     #             au = u.fitbitaccountuser
#     #             print("FitbitAccountUser type: " + str(type(au)))
#     #             print("FitbitAccountUser ID: " + str(au.user_id))
#     #         except FitbitAccountUser.DoesNotExist:
#     #             print("No FitbitAccountUser for " + str(u.id))
#     #         # a = au.fitbitaccount
#     #         # print("FitbitAccount: " + a.uuid)
#     #         # m = a.fitbitminutestepcount
#     #         # print("StepCount: " + str(a.steps))
#     #     else:
#     #         print("No user record for participant " + p.heartsteps_id)

#     return render(request, 'dashboard/index.html', context)

