from rest_framework import serializers
from .models import User, Otp
import math
import random
from datetime import datetime, timezone
from django.conf import settings
from django.core.mail import send_mail
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import update_last_login

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

EMAIL_HOST_USER = settings.EMAIL_HOST_USER
OTP_EXPIRED = settings.OTP_EXPIRED


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    otp_type = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        otp_type = data.get("otp_type", None)
        user = User.objects.filter(email=email, password=password).exists()
        if not user:
            raise serializers.ValidationError(
                'A user with this email and password is not found.'
            )
        try:
            user = User.objects.get(email=email)
            if user:
                generate_otp(user, otp_type)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exists'
            )
        return {'email': user.email}


def generate_otp(user, otp_type):
    # clear all previous otps of a user if present
    user_otps = Otp.objects.filter(user_id=user.id).all()
    try:
        if user_otps:
            user_otps.delete()

        # otp length is 4 digits random.randint(start,end)
        otp = str(random.randint(1000, 9999))
        verification_otp = Otp(user_id=user.id, otp_type=otp_type, otp=otp)
        verification_otp.save()
        subject = 'Verify email'
        message = ("Hello " + user.name + ",\n\nPlease use the following otp to verify your account:\n" + otp)
        send_mail(subject, message, user.email, [EMAIL_HOST_USER], fail_silently=False)

        return True
    except Exception as e:
        print(e)
        return False


class VerifyOtpSerializer(serializers.Serializer):
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
        if not user:
            raise serializers.ValidationError(
                'A user with this email and password is not found.'
            )
        try:
            user = User.objects.get(email=email)
            otp_verify = Otp.objects.filter(user_id=user.id, otp_type=otp_type, otp=otp).exists()

            if otp_verify:
                otp_verify = Otp.objects.filter(user_id=user.id, otp_type=otp_type, otp=otp).get()
                if (datetime.now(timezone.utc) - otp_verify.created_at).total_seconds() > OTP_EXPIRED:
                    raise serializers.ValidationError('Otp Expired')
                else:
                    payload = JWT_PAYLOAD_HANDLER(user)
                    jwt_token = JWT_ENCODE_HANDLER(payload)
                    update_last_login(None, user)
            else:
                raise serializers.ValidationError(
                    'Please enter correct otp'
                )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exists'
            )
        return {'email': user.email, 'token': jwt_token}
