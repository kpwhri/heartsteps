from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response

from .models import ActivityType

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def activity_types(request):
    activity_types = []
    for activity_type in ActivityType.objects.all():
        activity_types.append({
            'name': activity_type.name,
            'title': activity_type.title
        })
    return Response(activity_types, status=status.HTTP_200_OK)
