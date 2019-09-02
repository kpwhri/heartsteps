from django.http import Http404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from .models import Decision
from .models import DecisionRating

class DecisionRatingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DecisionRating
        fields = ('liked', 'comments')
        extra_kwargs = {
            'comments': {
                'allow_blank': True
            }
        }

class DecisionRatingView(APIView):

    permission_classes = (IsAuthenticated,)

    def get_decision(self, request, decision_id):
        try:
            return Decision.objects.get(
                user = request.user,
                id = decision_id
            )
        except Decision.DoesNotExist:
            raise Http404('Activity suggestion decision does not exist')

    def get(self, request, decision_id):
        decision = self.get_decision(request, decision_id)
        rating = decision.rating
        if decision.rating:
            serialized = DecisionRatingSerializer(decision.rating)
            return Response(serialized.data)
        return Response('No rating found', status=status.HTTP_404_NOT_FOUND)

    def post(self, request, decision_id):
        decision = self.get_decision(request, decision_id)
        serialized = DecisionRatingSerializer(data=request.data)
        if serialized.is_valid():
            DecisionRating.objects.update_or_create(
                decision = decision,
                defaults = serialized.validated_data
            )
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
