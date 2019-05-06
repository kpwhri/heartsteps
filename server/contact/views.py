from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers

from .models import ContactInformation

class ContactInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInformation
        fields = ('name', 'email', 'phone')

class ContactInformationView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        try:
            contact_information = ContactInformation.objects.get(user=request.user)
            serialized = ContactInformationSerializer(contact_information)
            return Response(serialized.data, status=status.HTTP_200_OK)
        except ContactInformation.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, format=None):
        serialized = ContactInformationSerializer(data=request.data)
        if serialized.is_valid():
            contact_information, created = ContactInformation.objects.get_or_create(user=request.user)
            
            contact_information.name = serialized.validated_data['name']
            contact_information.email = serialized.validated_data['email']
            contact_information.phone = serialized.validated_data['phone']
            contact_information.save()

            return Response(serialized.data, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

