from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import *
from .serializers import UserLoginSerializer


# Create your views here.

class Login(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status_code = status.HTTP_200_OK
        return Response(
            {'success': 'True', 'message': 'login mail send successfully'}, status=status_code)


class Otp_verify(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status_code = status.HTTP_200_OK
        return Response(
            {'success': 'True', 'message': 'Verify email successfully', 'token': serializer.data['token'], },
            status=status_code)
