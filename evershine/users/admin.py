from django.contrib import admin
from .models import *
# from django.contrib.auth.admin import UserAdmin
# from django.dispatch import receiver
# from django.db.models.signals import post_save

# Register your models here.
admin.site.register(Organization)


# admin.site.register(User)

# @receiver(post_save, sender=User)
# def save(sender, **kwargs):
#     user = kwargs.get('instance', None)
#     created = kwargs.get('created', False)
#     raw = kwargs.get('raw', False)
#     user.set_password(user.password)
#     print(user.password)
#     return user

# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         import pdb;
#         pdb.set_trace()
#         print(instance)
#         User.objects.create(user=instance)
#
#
#
#
# post_save.connect(create_profile, sender=User)

admin.site.register(User)
