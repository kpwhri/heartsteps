from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from django.utils import timezone

from .models import Place, Location

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('address', 'latitude', 'longitude', 'type')

class PlacesView(APIView):
    """
    Accepts or rejects a list of places specified for a user
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):        
        places = Place.objects.filter(user=request.user).all()
        serializer = PlaceSerializer(places, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = PlaceSerializer(data=request.data, many=True)
        if serializer.is_valid():
            Place.objects.filter(user=request.user).delete()
            for place in serializer.validated_data:
                placeObj = Place(
                    user = request.user,
                    latitude = place['latitude'],
                    longitude = place['longitude'],
                    type = place['type']
                )
                if 'address' in place:
                    placeObj.address = place['address']
                placeObj.save()
            return Response(
                serializer.validated_data,
                status=status.HTTP_201_CREATED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('latitude', 'longitude', 'source')

class LocationUpdateView(APIView):
    """
    Updates a user's location
    """

    def post(self, request):
        serialized = LocationSerializer(data=request.data)
        if serialized.is_valid():
            location = Location(**serialized.validated_data)
            location.user = request.user
            location.time = timezone.now()
            location.save()
            return Response({}, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
