from django.shortcuts import render

from django.contrib.auth.models import User
from participants.models import Participant
from contact.models import ContactInformation
from fitbit_activities.models import FitbitMinuteStepCount
from fitbit_api.models import FitbitAccount, FitbitAccountUser

def index(request):
    participant_list = Participant.objects.all().prefetch_related('user').order_by('heartsteps_id')
    context = {'participant_list': participant_list}

    # a = FitbitMinuteStepCount.objects
    # print("Count: " + str(a.count()))
    # b = a.filter(fitbitaccount__fitbit_user='6S2PTQ')
    # print(b)
    # print("Count: " + str(b.count()))

    n = 0
    for p in participant_list:
        n += 1
        print("Participant #" + str(n))
        u = p.user
        if u:
            print("User ID: " + str(u.id))

            try:
                au = u.fitbitaccountuser
                print("FitbitAccountUser type: " + str(type(au)))
                print("FitbitAccountUser ID: " + str(au.user_id))
            except FitbitAccountUser.DoesNotExist:
                print("No FitbitAccountUser for " + str(u.id))
            # a = au.fitbitaccount
            # print("FitbitAccount: " + a.uuid)
            # m = a.fitbitminutestepcount
            # print("StepCount: " + str(a.steps))
        else:
            print("No user record for participant " + p.heartsteps_id)

    return render(request, 'dashboard/index.html', context)
