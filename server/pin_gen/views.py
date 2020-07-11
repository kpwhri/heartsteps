from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token

import random

from django.contrib.auth.models import User
from .models import Pin


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
