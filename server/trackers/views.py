from django.contrib.auth import login
from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework import status, permissions
from rest_framework.response import Response
from django.shortcuts import redirect

@api_view(['GET'])
def authorize(request, username):
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        login(request, user)
        return redirect('fitbit-login')
    return Response({}, status=status.HTTP_400_BAD_REQUEST)
        