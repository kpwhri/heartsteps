from datetime import datetime
from unittest import signals
import pytz

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ClockFace
from .models import ClockFaceStepCount
from .models import User
from .signals import step_count_updated

class CreateClockFace(APIView):

    def post(self):
        clock_face = ClockFace.objects.create()
        return Response({
            'pin': clock_face.pin,
            'token': clock_face.token
        })

class ClockFaceStatus(APIView):

    def get(self, request):
        if 'HTTP_CLOCK_FACE_PIN' in request.META and 'HTTP_CLOCK_FACE_TOKEN' in request.META:
            try:
                clock_face = ClockFace.objects.get(
                    pin = request.META['HTTP_CLOCK_FACE_PIN'],
                    token = request.META['HTTP_CLOCK_FACE_TOKEN']
                )
                username = None
                if clock_face.user:
                    username = clock_face.user.username
                username = clock_face.user
                return Response({
                    'paired': clock_face.paired,
                    'pin': clock_face.pin,
                    'token': clock_face.token,
                    'username': clock_face.username
                })
            except ClockFace.DoesNotExist:
                pass
        return Response('Pin and Token Invalid', status=status.HTTP_401_UNAUTHORIZED)

class ClockFacePair(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            clock_face = ClockFace.objects.get(
                user = request.user
            )
            return Response({
                'pin': clock_face.pin,
                'created': clock_face.created
            })
        except ClockFace.DoesNotExist:
            return Response('No matching clock face', status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if 'pin' in request.data:
            try:
                clock_face = ClockFace.objects.get(
                    pin = request.data['pin']
                )
                if clock_face.user is not None:
                    if clock_face.user.id == request.user.id:
                        return Response({
                            'pin': clock_face.pin,
                            'token': clock_face.token
                        })
                    else:
                        return Response('Clock face not available', status=status.HTTP_400_BAD_REQUEST)
                else:
                    ClockFace.objects.filter(user = request.user).delete()
                clock_face.user = request.user
                clock_face.save()
                return Response({
                    'pin': clock_face.pin,
                    'created': clock_face.created
                }, status=status.HTTP_201_CREATED)
            except ClockFace.DoesNotExist:
                return Response('Clock Face Pin Not Found', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Need pin', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            clock_face = ClockFace.objects.get(
                user = request.user
            )
            clock_face.delete()
            return Response('Deleted', status=status.HTTP_200_OK)
        except ClockFace.DoesNotExist:
            return Response('Not found', status=status.HTTP_404_NOT_FOUND)



class ClockFaceStepCounts(APIView):

    def get(self, request):

        if request.user.is_authenticated():
            step_counts = []
            for step_count in ClockFaceStepCount.objects.filter(user=request.user).order_by('-end')[:10]:
                step_counts.append({
                    'time': step_count.time.isoformat(),
                    'steps': step_count.steps
                })
            return Response({
                'step_counts': step_counts
            })

        else:
            return Response('Not authorized', status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        if 'HTTP_CLOCK_FACE_PIN' in request.META and 'HTTP_CLOCK_FACE_TOKEN' in request.META:
            try:
                clock_face = ClockFace.objects.prefetch_related('user').get(
                    pin = request.META['HTTP_CLOCK_FACE_PIN'],
                    token = request.META['HTTP_CLOCK_FACE_TOKEN']
                )
                if clock_face.user:
                    if 'step_counts' in request.data and isinstance(request.data['step_counts'], list):
                        for step_count in request.data['step_counts']:
                            time = datetime.utcfromtimestamp(step_count['time']/1000).astimezone(pytz.UTC)
                            ClockFaceStepCount.objects.update_or_create(
                                time = time,
                                user = clock_face.user,
                                defaults= {
                                    'steps': step_count['steps']
                                }
                            )
                        step_count_updated.send(User, username=clock_face.user.username)
                        return Response('', status=status.HTTP_201_CREATED)
                    return Response('step_counts not included', status=status.HTTP_400_BAD_REQUEST)
            except ClockFace.DoesNotExist:
                pass
        return Response('Pin and Token Invalid', status=status.HTTP_401_UNAUTHORIZED)
