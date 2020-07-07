from django.shortcuts import render
from django.http import JsonResponse
import random


def index(request):
	num = random.randint(0, 99999)
	# add padding if necessary
	randVal = str(num)
	if (num < 10000):
		randVal = randVal.zfill(5)
	return JsonResponse({'pin': randVal}, status=200)

def pinArray(request):
	num = list(range(0, 10))
	a = [None] * 5
	for i in range(5):
		index = random.randint(0, 9)
		a[i] = index
		
	return JsonResponse({'pin': a}, status=200)


