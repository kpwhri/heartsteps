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


#MY CODE (without Token); extremely rough draft
def pinA(self):
	a = getArray()
	return JsonResponse({'pin': a}, status=200)

@api_view(['GET', 'POST'])
def user(request):
	p = request.data["pin"]
	
	d = 0
	for i in p:
		if (i.isnumeric()):
			d += int(i)
			d *= 10
	d /= 10

	try:
		p = Pin.objects.get(pin_digits=d)
	except Pin.DoesNotExist:
		return JsonResponse({'pin': "", "Exist": False }, status=200)

	try:
		t = Token.objects.get(user=p.user)
		print(t.key)
		return JsonResponse({ "Token" : t.key, "Exist": True }, status=200)
	except:
		return JsonResponse({"Exist": False }, status=200)
		



