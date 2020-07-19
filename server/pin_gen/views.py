import random

from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from .models import Pin
from .models import ClockFacePin


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pinArray(request):
	a = getArray()
		

	return JsonResponse({'pin': a, 'authenticated': request.user.is_authenticated}, status=200)


def getArray():
	num = list(range(0, 10))
	a = [None] * 5
	for i in range(5):
		index = random.randint(0, 9)
		a[i] = index
	return a

class PinSerializer(serializers.Serializer):
	pin = serializers.CharField()

class ClockFacePinView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		try:
			pin = ClockFacePin.objects.get(user = request.user)
			return Response({
				'pin': pin.pin
			})
		except ClockFacePin.DoesNotExist:
			return Response('No pin', status=status.HTTP_404_NOT_FOUND)

	def post(self, request):
		serializer = PinSerializer(data=request.data)
		if serializer.is_valid():
			pin = serializer.validated_data['pin']
			try:
				pin = ClockFacePin.objects.get(pin = pin)
				pin.user = request.user
				pin.save()
				return Response({
					'pin': pin.pin
				})
			except ClockFacePin.DoesNotExist:
				return Response('Pin does not exist', status=status.HTTP_400_BAD_REQUEST)
		else: 
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
