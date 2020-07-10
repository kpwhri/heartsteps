from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
import random

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pinArray(request):
	num = list(range(0, 10))
	a = [None] * 5
	for i in range(5):
		index = random.randint(0, 9)
		a[i] = index
		
	print(request.user.is_authenticated)
	return JsonResponse({'pin': a, 'authenticated': request.user.is_authenticated}, status=200)


