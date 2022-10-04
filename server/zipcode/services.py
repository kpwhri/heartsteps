import requests
from locations.models import Location
from zipcode.models import ZipCodeRequestHistory
from system_settings.models import SystemSetting
from django.utils import timezone

class ZipCodeService:
    def __init__(self) -> None:
        pass

    def fill_location_info_offline(user, zipcode, lat, lon, state, city):
        request_obj = ZipCodeRequestHistory()
        request_obj.user = user
        request_obj.zipcode = zipcode

        request_obj.response_code = "200"
        request_obj.response_message = "offline"

        request_obj.latitude = lat
        request_obj.longitude = lon
        request_obj.state = state
        request_obj.city = city
        request_obj.save()

        query = Location.objects.filter(user=user)
        
        if query.exists():
            location = query.first()
            location.latitude = lat
            location.longitude = lon
            location.time = timezone.now()
            location.category = "Home"
            location.save()
        else:
            location = Location.objects.create(
                user=user,
                latitude=lat,
                longitude=lon,
                time=timezone.now(),
                category="Home"
            )
        
        return location
        
    def fill_location_info(user, zipcode):
        api_key = SystemSetting.get('ZIPCODE_API_KEY')
        url = "https://www.zipcodeapi.com/rest/{}/info.json/{}/degrees".format(api_key, zipcode)


        request_obj = ZipCodeRequestHistory()
        request_obj.user = user
        request_obj.zipcode = zipcode

        response = requests.get(url)
        request_obj.response_code = response.status_code
        request_obj.response_message = response.text

        if response.status_code is not 200:
            raise RuntimeError("ZipCode Fetch Error: HTTP code={}, response.text={}, user={}, zipcode={}".format(response.status_code, response.text, user, zipcode))

        zipcode_json = response.json()
        
        request_obj.latitude = zipcode_json['lat']
        request_obj.longitude = zipcode_json['lng']
        request_obj.state = zipcode_json['state']
        request_obj.city = zipcode_json['city']
        request_obj.save()

        query = Location.objects.filter(user=user)
        
        if query.exists():
            location = query.first()
            location.latitude = zipcode_json['lat']
            location.longitude = zipcode_json['lng']
            location.time = timezone.now()
            location.category = "Home"
            location.save()
        else:
            location = Location.objects.create(
                user=user,
                latitude=zipcode_json['lat'],
                longitude=zipcode_json['lng'],
                time=timezone.now(),
                category="Home"
            )
        
        return location