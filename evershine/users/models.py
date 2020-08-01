from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import User
from datetime import datetime, timezone
from passlib.hash import pbkdf2_sha256


# Create your models here.

class Organization(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    use_in_migrations = True

    # def create_user(self, name, email, password=None):
    #     if not email:
    #         raise ValueError('Users Must Have an email address')
    #     user = self.model(name=name, email=email)
    #     user.set_password(password)
    #     user.save()
    #     return user

    def create_superuser(self, full_name, email, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        # user = self.create_user(name, email, password)
        user = self.model(full_name=full_name, email=email)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=254)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return self.email


class Projects(models.Model):
    project_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User F.K.
    project_owner = models.CharField(max_length=255)  # User Name
    status = models.CharField(max_length=255)
    remark = models.CharField(max_length=555)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)  # only org. related person show all the projects
    created_at = models.DateTimeField(auto_now=True)


class Plants(models.Model):
    plant_name = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    responsible_person = models.CharField(max_length=255)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    # user = models.ForeignKey(User, on_delete=models.CASCADE) # Project owner is also a responsible person
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)
    remark = models.CharField(max_length=255)
    is_simulation = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)


class Otp(models.Model):
    otp_type = models.CharField(max_length=100)
    otp = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
