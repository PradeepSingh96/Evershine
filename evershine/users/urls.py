from users import views
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from users import views

urlpatterns = [
    url(r"^login/", views.Login.as_view(), name='Login'),
    url(r"^verify_otp/", views.Otp_verify.as_view(), name='Otp_verify'),
    url(r"^forget/", views.Forget_password.as_view(), name='Forget_password'),
    url(r"^reset/", views.Reset_password.as_view(), name='Reset_password'),
]
