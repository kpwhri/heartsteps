from django.http import HttpResponse
from django.shortcuts import render
import requests

TEST_URL = 'https://jsonplaceholder.typicode.com/posts'
FITBIT_PROFILE_URL = 'https://api.fitbit.com/1/user/[user-id]/profile.json'
FITBIT_WEIGHT_URL = 'https://api.fitbit.com/1/user/[user-id]/body/log/weight/date/[access-date]/30d.json'
FITBIT_DAILY_ACTIVITY_URL = 'https://api.fitbit.com/1/user/[user-id]/activities/date/[access-date].json'
FITBIT_MINUTE_STEP_URL = 'https://api.fitbit.com/1/user/[user-id]/activities/steps/date/[access-date]/1d.json'
FITBIT_DAILY_FOOD_URL = 'https://api.fitbit.com/1/user/[user-id]/foods/log/date/[access-date].json'
FITBIT_SLEEP_URL = 'https://api.fitbit.com/1.2/user/[user-id]/sleep/date/[access-date]/[access-plus-30-date].json'
FITBIT_HEART_RATE_URL = 'https://api.fitbit.com/1/user/[user-id]/activities/heart/date/[access-date]/1d/1min.json'


class HttpResponseNoContent(HttpResponse):
    status_code = 204


def test(request):
    """
    Test basic GET functionality
    """
    request_url = TEST_URL
    response = requests.get(request_url)
    content = response.json()
    for data in content:
        print(f'userID: {data["userId"]}')
        print(f'id: {data["id"]}')
        print(f'title: {data["title"]}')
        print(f'body: {data["body"]}')
    return HttpResponseNoContent()


def device(request):
    """
    GET device data
    """
    request_url = DEVICE_URL
    request_url = request_url.replace("[user-id]", participant.tracker_id)

    headers = {
        'Authorization': 'Bearer ' + participant.access_token,
        'Accept-Language': 'en_US'
    }
    response = requests.get(request_url, headers=headers)
    content = response.json()
    for data in content:
        device = Tracker(user=user.id, device_type=data['type'],
                         battery=data['battery'], device_version=data['deviceVersion'],
                         last_sync_dtm=data['lastSyncTime'])
        device.save()
    return HttpResponseNoContent()
