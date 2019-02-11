from rest_framework.views import APIView

from rest_framework import status, permissions
from rest_framework.response import Response

from .models import ActivityType

class ActivityTypesList(APIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        activity_types = []
        for activity_type in ActivityType.objects.filter(user=None).all():
            activity_types.append({
                'name': activity_type.name,
                'title': activity_type.title
            })
        for activity_type in ActivityType.objects.filter(user=request.user).all():
            activity_types.append({
                'name': activity_type.name,
                'title': activity_type.title
            })
        return Response(activity_types, status=status.HTTP_200_OK)

    def post(self, request):
        if 'name' in request.data:
            activity_type, created = ActivityType.objects.get_or_create(
                name = request.data['name'].lower(),
                title = request.data['name'],
                user = request.user
            )
            type_data = {
                'name': activity_type.name,
                'title': activity_type.title
            }
            if created:
                return Response(type_data, status=status.HTTP_201_CREATED)
            else:
                return Response(type_data, status=status.HTTP_200_OK)
        else:
            return Response('Bad request', status=status.HTTP_400_BAD_REQUEST)




