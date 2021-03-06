from rest_framework import serializers
from .models import User, Otp
import math
import random
from datetime import datetime, timezone
from django.conf import settings
from django.core.mail import send_mail
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from itsdangerous import URLSafeTimedSerializer
from django.contrib.auth import authenticate
import secrets
import string
from .models import *

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

EMAIL_HOST_USER = settings.EMAIL_HOST_USER
SECRET_KEY = settings.SECRET_KEY
OTP_EXPIRED = settings.OTP_EXPIRED
HOST = settings.FRONT_END_URL


class GenerateOtpSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128)
    otp_type = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        otp_type = data.get("otp_type", None)
        project_id = None
        plant_id = None
        user = User.objects.filter(email=email, password=password).exists()
        # user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError(
                'Incorrect email address or password. Please try again.'
            )
        try:
            user = User.objects.get(email=email)
            if user:
                generate_otp(user, otp_type, project_id, plant_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Incorrect email address or password. Please try again.'
            )
        return {'email': user.email, 'password': user.password}


class ProjectOtpSerializer(serializers.Serializer):
    otp_type = serializers.CharField(max_length=128, write_only=True)
    project_id = serializers.CharField(max_length=128)

    def validate(self, data):
        otp_type = data.get("otp_type", None)
        project_id = data.get("project_id", None)
        request = self.context.get("request")
        user = request.user
        try:
            plant_id=None
            user = User.objects.get(email=user.email)
            if user:
                generate_otp(user, otp_type, project_id, plant_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Incorrect email address or password. Please try again.'
            )
        return {'email': user.email, 'project_id': project_id}


class PlantOtpSerializer(serializers.Serializer):
    otp_type = serializers.CharField(max_length=128, write_only=True)
    project_id = serializers.CharField(max_length=128)
    plant_id = serializers.CharField(max_length=128)

    def validate(self, data):
        otp_type = data.get("otp_type", None)
        project_id = data.get("project_id", None)
        plant_id = data.get("plant_id", None)
        request = self.context.get("request")
        user = request.user
        try:
            user = User.objects.get(email=user.email)
            if user:
                generate_otp(user, otp_type, project_id, plant_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Incorrect email address or password. Please try again.'
            )
        return {'email': user.email, 'project_id': project_id, 'plant_id': plant_id}


def generate_otp(user, otp_type, project_id, plant_id):
    # clear all previous otps of a user if present
    user_otps = Otp.objects.filter(user_id=user.id, project_id=project_id, plant_id=plant_id).all()
    if user_otps:
        user_otps.delete()
    # otp length is 4 digits random.randint(start,end)
    otp = str(random.randint(1000, 9999))

    try:
        verification_otp = Otp(user_id=user.id, otp_type=otp_type, otp=otp, project_id=project_id, plant_id=plant_id)
        verification_otp.save()
        if otp_type == "verify_email":
            subject = 'Verify email'
            message = ("Hello " + user.full_name + ",\n\nPlease use the following otp to verify your account:\n" + otp)
            send_mail(subject, message, EMAIL_HOST_USER, [user.email], fail_silently=False)
        if otp_type == "delete_project":
            subject = 'Delete Project'
            message = ("Hello " + user.full_name + ",\n\nPlease use the following otp to delete your project:\n" + otp)
            send_mail(subject, message, EMAIL_HOST_USER, [user.email], fail_silently=False)
        if otp_type == "edit_project":
            subject = 'Edit Project'
            message = (
                    "Hello " + user.full_name + ",\n\nPlease use the following otp to edit your project details:\n" + otp)
            send_mail(subject, message, EMAIL_HOST_USER, [user.email], fail_silently=False)
        if otp_type == "delete_plant":
            subject = 'Delete Plant'
            message = ("Hello " + user.full_name + ",\n\nPlease use the following otp to delete your plant:\n" + otp)
            send_mail(subject, message, EMAIL_HOST_USER, [user.email], fail_silently=False)
        return True
    except Exception as e:
        raise serializers.ValidationError(str(e))


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    otp_type = serializers.CharField(max_length=128, write_only=True)
    otp = serializers.CharField(max_length=125, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):

        email = data.get("email", None)
        password = data.get("password", None)
        otp_type = data.get("otp_type", None)
        otp = data.get("otp", None)

        user = User.objects.filter(email=email, password=password).exists()
        # user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError(
                'Incorrect email address or password. Please try again.'
            )
        try:
            user = User.objects.get(email=email)
            otp_verify = Otp.objects.filter(user_id=user.id, otp_type=otp_type, otp=otp).exists()

            if otp_verify:
                otp_verify = Otp.objects.filter(user_id=user.id, otp_type=otp_type, otp=otp).get()
                # if Otp time is > 30 min Otp Expire
                if (datetime.now(timezone.utc) - otp_verify.created_at).total_seconds() > OTP_EXPIRED:
                    raise serializers.ValidationError('Otp Expired')
                else:
                    payload = JWT_PAYLOAD_HANDLER(user)
                    jwt_token = JWT_ENCODE_HANDLER(payload)
                    update_last_login(None, user)
            else:
                raise serializers.ValidationError(
                    'Please Enter Correct OTP'
                )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Incorrect email address or password. Please try again.'
            )
        return {'email': user.email, 'token': jwt_token, 'password': password}


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)

    def validate(self, data):

        email = data.get("email", None)
        user = User.objects.filter(email=email).exists()
        if not user:
            raise serializers.ValidationError(
                'Incorrect email address or password. Please try again.'
            )
        try:
            user = User.objects.filter(email=email).get()
            # alphabet = string.ascii_letters + string.digits
            # password = ''.join(secrets.choice(alphabet) for i in range(15))
            # user.set_password(password)
            # user.save()
            link = 'http://' + HOST + '/reset/' + generate_confirmation_token(user.email)
            if not link:
                raise serializers.ValidationError(
                    'The link has expired. Please click on forgot password to generate a new link'
                )
            subject = 'Reset Password'
            message = ("Hello " + user.full_name + ",\n\nPlease click on the following link to reset your password:\n")

            email_send = send_mail(subject, message + link, EMAIL_HOST_USER, [user.email], fail_silently=False, )
            if not email_send:
                raise serializers.ValidationError(
                    'Recovery Email Failed'
                )

        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Incorrect email address or password. Please try again.'
            )
        return {'email': user.email}


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email)


class RestPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
    confirm_password = serializers.CharField(max_length=255)

    def validate(self, data):
        token = data.get("token", None)
        password = data.get("password", None)
        confirm_password = data.get("confirm_password", None)

        email = confirm_token(token)
        if not email:
            raise serializers.ValidationError(
                'Invalid Token'
            )
        try:
            user = User.objects.filter(email=email).get()
            # user.set_password(password)
            if password == confirm_password:
                user.password = password
                user.save()
            else:
                raise serializers.ValidationError(
                    'Password Not Matched'
                )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Password reset failed'
            )
        return {'email': user.email}


def confirm_token(token, expiration=120):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(token, max_age=expiration)
    except:
        return False
    return email


class AddProjectSerializer(serializers.Serializer):
    project_name = serializers.CharField(max_length=255)
    status = serializers.CharField(max_length=255)
    remark = serializers.CharField(max_length=555)

    def validate(self, data):

        project_name = data.get("project_name", None)
        status = data.get("status", None)
        remark = data.get("remark", None)
        request = self.context.get("request")
        user = request.user
        try:
            user = User.objects.filter(email=user.email).get()
            project = Projects(project_name=project_name, status=status, remark=remark, user_id=user.id,
                               project_owner=user.full_name, organization=user.organization)
            project.save()
        except User.DoesNotExist:
            raise serializers.ValidationError('Project not added')
        return True


class GetProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = '__all__'


class DeleteProjectSerializer(serializers.Serializer):
    otp_type = serializers.CharField(max_length=128, write_only=True)
    otp = serializers.CharField(max_length=125, write_only=True)
    project_id = serializers.CharField(max_length=255, write_only=True)

    def validate(self, data):

        otp_type = data.get("otp_type", None)
        otp = data.get("otp", None)
        project_id = data.get("project_id", None)
        request = self.context.get("request")
        user = request.user
        try:
            # user = User.objects.get(email=email)
            otp_verify = Otp.objects.filter(user_id=user.id, otp_type=otp_type, otp=otp, project_id=project_id).exists()

            if otp_verify:
                otp_verify = Otp.objects.filter(user_id=user.id, otp_type=otp_type, otp=otp,
                                                project_id=project_id).get()
                # if Otp time is > 30 min Otp Expire
                if (datetime.now(timezone.utc) - otp_verify.created_at).total_seconds() > OTP_EXPIRED:
                    raise serializers.ValidationError('Otp Expired')
                else:
                    project = Projects.objects.filter(id=project_id, user_id=user.id).exists()
                    if not project:
                        raise serializers.ValidationError(
                            'Only Project Owner delete the project'
                        )
                    project = Projects.objects.filter(id=project_id, user_id=user.id).get()
                    project.delete()
            else:
                raise serializers.ValidationError(
                    'Please Enter Correct OTP'
                )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Incorrect email address or password. Please try again.'
            )
        return True


class EditProjectSerializer(serializers.Serializer):
    otp_type = serializers.CharField(max_length=128, write_only=True)
    otp = serializers.CharField(max_length=125, write_only=True)
    project_id = serializers.CharField(max_length=255, write_only=True)
    project_name = serializers.CharField(max_length=255, write_only=True)
    status = serializers.CharField(max_length=255, write_only=True)
    remark = serializers.CharField(max_length=255, write_only=True)

    def validate(self, data):

        otp_type = data.get("otp_type", None)
        otp = data.get("otp", None)
        project_id = data.get("project_id", None)
        project_name = data.get("project_name", None)
        status = data.get("status", None)
        remark = data.get("remark", None)
        request = self.context.get("request")
        user = request.user
        try:
            # user = User.objects.get(email=email)
            otp_verify = Otp.objects.filter(user_id=user.id, otp_type=otp_type, otp=otp, project_id=project_id).exists()

            if otp_verify:
                otp_verify = Otp.objects.filter(user_id=user.id, otp_type=otp_type, otp=otp,
                                                project_id=project_id).get()
                # if Otp time is > 30 min Otp Expire
                if (datetime.now(timezone.utc) - otp_verify.created_at).total_seconds() > OTP_EXPIRED:
                    raise serializers.ValidationError('Otp Expired')
                else:
                    project = Projects.objects.filter(id=project_id, user_id=user.id).exists()
                    if not project:
                        raise serializers.ValidationError(
                            'Only Project Owner Edit the project details'
                        )
                    project = Projects.objects.filter(id=project_id, user_id=user.id).get()
                    if project_name == "None":
                        project_name = project.project_name
                    if status == "None":
                        status = project.status
                    if remark == "None":
                        remark = project.remark

                    project.project_name = project_name
                    project.status = status
                    project.remark = remark
                    project.user_id = user.id
                    project.project_owner = user.full_name
                    project.save()
            else:
                raise serializers.ValidationError(
                    'Please Enter Correct OTP'
                )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Incorrect email address or password. Please try again.'
            )
        return True


# Add Plant Serializer
class AddPlantSerializer(serializers.Serializer):
    plant_name = serializers.CharField(max_length=255, write_only=True)
    size = serializers.CharField(max_length=255, write_only=True)
    location = serializers.CharField(max_length=255, write_only=True)
    status = serializers.CharField(max_length=255, write_only=True)
    remark = serializers.CharField(max_length=255, write_only=True)
    is_simulation = serializers.CharField(max_length=255, write_only=True)
    project_id = serializers.CharField(max_length=255, write_only=True)

    parent_id = serializers.CharField(max_length=255, write_only=True, default=None)

    def validate(self, data):

        plant_name = data.get("plant_name", None)
        size = data.get("size", None)
        location = data.get("location", None)
        project_id = data.get("project_id", None)
        status = data.get("status", None)
        remark = data.get("remark", None)
        is_simulation = data.get("is_simulation", None)
        parent_id = data.get("parent_id", None)
        request = self.context.get("request")
        user = request.user
        try:
            user = User.objects.filter(email=user.email).get()
            project = Projects.objects.filter(id=project_id).get()
            if not project:
                raise serializers.ValidationError('Please select Project')
            # responsible_person is Also user who logged in
            plant = Plants(plant_name=plant_name, size=size, location=location, responsible_person=user.full_name,
                           project_id=project.id, status=status, remark=remark, user_id=user.id,
                           organization=user.organization, is_simulation=is_simulation, parent_id=parent_id)
            plant.save()
            print('plant saved', flush=True)
        except User.DoesNotExist:
            raise serializers.ValidationError('Plant not added')
        return True


class GetPlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plants
        fields = '__all__'


# Delete Plants
class DeletePlantSerializer(serializers.Serializer):
    otp_type = serializers.CharField(max_length=128, write_only=True)
    otp = serializers.CharField(max_length=125, write_only=True)
    project_id = serializers.CharField(max_length=255, write_only=True)
    plant_id = serializers.CharField(max_length=255, write_only=True)

    def validate(self, data):

        otp_type = data.get("otp_type", None)
        otp = data.get("otp", None)
        project_id = data.get("project_id", None)
        plant_id = data.get("plant_id", None)
        request = self.context.get("request")
        user = request.user
        try:
            # user = User.objects.get(email=email)
            otp_verify = Otp.objects.filter(user_id=user.id, otp_type=otp_type, otp=otp, plant_id=plant_id, project_id=project_id).exists()

            if otp_verify:
                otp_verify = Otp.objects.filter(user_id=user.id, otp_type=otp_type, otp=otp,
                                                plant_id=plant_id, project_id=project_id).get()
                # if Otp time is > 30 min Otp Expire
                if (datetime.now(timezone.utc) - otp_verify.created_at).total_seconds() > OTP_EXPIRED:
                    raise serializers.ValidationError('Otp Expired')
                else:
                    sub_plant = Plants.objects.filter(project_id=project_id, parent_id=plant_id).exists()
                    if sub_plant:
                        sub_plant = Plants.objects.filter(project_id=project_id, parent_id=plant_id).all()
                        sub_plant.delete()
                    plant = Plants.objects.filter(id=plant_id, user_id=user.id, project_id=project_id).exists()
                    if not plant:
                        raise serializers.ValidationError(
                            'Only Plant Owner delete the Plant'
                        )
                    plant = Plants.objects.filter(id=plant_id, user_id=user.id, project_id=project_id).get()
                    plant.delete()
            else:
                raise serializers.ValidationError(
                    'Please Enter Correct OTP'
                )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Incorrect email address or password. Please try again.'
            )
        return True

