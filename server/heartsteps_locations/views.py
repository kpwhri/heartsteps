from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.core import serializers

from .models import Location

class LocationsView(APIView):
    """
    Accepts or rejects a list of locations specified for a user
    """
    permission_classes = (IsAuthenticated,)

    def serializeLocations(self, locations):
        serializedLocations = []
        for location in locations:
            serializedLocations.append({
                'address': location.address,
                'lat': location.lat,
                'long': location.long,
                'type': location.type
            })
        return serializedLocations

    def get(self, request, format=None):        
        locations = Location.objects.filter(user=user).all()
        data = self.serializeLocations(locations)
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        if request.data['locations']:
            Location.objects.filter(user=request.user).delete()
            locations = []
            for locationObj in request.data['locations']:
                location = Location.objects.create(
                    user = request.user,
                    address = locationObj['address'],
                    lat = locationObj['lat'],
                    long = locationObj['long'],
                    type = locationObj['type']
                )
                locations.append(location)
            return Response(
                self.serializeLocations(locations),
                status=status.HTTP_201_CREATED
                )
        return Response({}, status=status.HTTP_400_BAD_REQUEST)
