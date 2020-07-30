from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import *
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


# Create your views here.
# Generate Otp
class Generate_Otp(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = GenerateOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status_code = status.HTTP_200_OK
        return Response(
            {'success': 'True', 'message': 'login mail send successfully'}, status=status_code)


# Login
class Login(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status_code = status.HTTP_200_OK
        return Response(
            {'success': 'True', 'message': 'Verify email successfully', 'token': serializer.data['token'], },
            status=status_code)


# Send forget password email
class Forget_password(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status_code = status.HTTP_200_OK
        return Response({'success': 'True', 'message': 'Recovery email sent successfully'}, status=status_code)


# Reset Password
# class Reset_password(APIView):
#     permission_classes = (AllowAny,)
#
#     def post(self, request):
#         serializer = RestPasswordSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         status_code = status.HTTP_200_OK
#         return Response({'success': 'True', 'message': 'Password change Successfully'}, status=status_code)

# Get All Projects Details
class Get_All_Projects(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        user = Projects.objects.all()
        serializer = GetProjectSerializer(user, many=True)
        return Response(serializer.data)


# Add Project
class Add_Project(APIView):
    permission_classes = (IsAuthenticated,)

    # authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        serializer = AddProjectSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        status_code = status.HTTP_200_OK
        return Response(
            {'success': 'True', 'message': 'Project add successfully'}, status=status_code)


# Project OTP
class Project_Generate_Otp(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ProjectOtpSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        status_code = status.HTTP_200_OK
        return Response(
            {'success': 'True', 'message': 'Otp send successfully'}, status=status_code)


# Delete Project
class Delete_Project(APIView):
    permission_classes = (IsAuthenticated,)

    # authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        serializer = DeleteProjectSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        status_code = status.HTTP_200_OK
        return Response(
            {'success': 'True', 'message': 'Project delete successfully'}, status=status_code)


class Edit_Project(APIView):
    permission_classes = (IsAuthenticated,)

    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request):
        data = request.data
        project = Projects.objects.filter(id=data.get('project_id'), user_id=request.user.id)
        serializer = GetProjectSerializer(project, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EditProjectSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        status_code = status.HTTP_200_OK
        return Response(
            {'success': 'True', 'message': 'Project details edited successfully'}, status=status_code)
