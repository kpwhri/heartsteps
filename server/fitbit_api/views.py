from datetime import timedelta

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response

from fitbit_api.utils import create_fitbit
from fitbit_api.models import FitbitAccount, AuthenticationSession

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def authorize_start(request):
    AuthenticationSession.objects.filter(user=request.user, disabled=False).update(disabled=True)
    session = AuthenticationSession.objects.create(user=request.user)
    return Response({
        'token': str(session.token)
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def authorize(request, token):
    if token:
        try:
            valid_time = timezone.now() - timedelta(hours=1)
            session = AuthenticationSession.objects.get(token=token, disabled=False, created__gt=valid_time)
        except AuthenticationSession.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        login(request, session.user)

        complete_url = request.build_absolute_uri(reverse('fitbit-authorize-process'))
        if not settings.DEBUG and 'https://' not in complete_url:
            complete_url = complete_url.replace('http://', 'https://')

        fitbit = create_fitbit()
        authorize_url, state = fitbit.client.authorize_token_url(redirect_uri=complete_url)
        
        session.state = state
        session.save()

        return redirect(authorize_url)
    return Response({}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def authorize_process(request):
    if 'code' in request.GET and 'state' in request.GET:
        try:
            valid_time = timezone.now() - timedelta(hours=1)
            session = AuthenticationSession.objects.get(
                state=request.GET['state'],
                disabled=False,
                created__gt=valid_time
                )
            user = session.user
        except AuthenticationSession.DoesNotExist:
            return redirect(reverse('fitbit-authorize-complete'))

        session.disabled = True
        session.save()

        code = request.GET['code']
        fitbit = create_fitbit()
        try:
            token = fitbit.client.fetch_access_token(code)
            access_token = token['access_token']
            fitbit_user = token['user_id']
            refresh_token = token['refresh_token']
            expires_at = token['expires_at']
        except KeyError:
            return redirect(reverse('fitbit-authorize-complete'))

        fitbit_account, _ = FitbitAccount.objects.update_or_create(user=user, defaults={
            'fitbit_user': fitbit_user,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at
        })
        
        return redirect(reverse('fitbit-authorize-complete'))
    return Response({}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def authorize_complete(request):
    return render(request, 'fitbit/index.html')
