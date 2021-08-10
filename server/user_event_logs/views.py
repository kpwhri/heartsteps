from django.shortcuts import render
from django.core.paginator import Paginator

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

# Create your views here.
from .models import EventLog

def in_range(value, min, max):
    if value > max:
        return max
    elif value < min:
        return min
    else:
        return value

class UserLogsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response("Not authenticated", status=status.HTTP_UNAUTHORIZED)
        
        # default page size is 10
        try:
            pagesize = in_range(int(request.GET.get('pagesize', 10)), 10, 100)
        except:
            pagesize = 10
        
        # default page number is 1
        try:
            page = int(request.GET.get('page', 1))
        except:
            page = 1
        
        user_logs = EventLog.objects.filter(
            user = request.user
        ).order_by('-timestamp') \
        .all()
        
        paginator = Paginator(user_logs, pagesize) 

        page_obj = paginator.get_page(page)
        
        # if you don't have any log, you might want to see empty logs with 200, not 404. 404 usually means you're knocking on non-existing door.
        serialized_user_logs = []
        for user_log in page_obj:
            serialized_user_logs.append({
                'timestamp': user_log.timestamp,
                'status': user_log.status,
                'action': user_log.action
            })
        return Response({'logs': serialized_user_logs, 'page': page, 'max_page': paginator.num_pages})

