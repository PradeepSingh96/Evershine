from users import views
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from users import views

urlpatterns = [
    url(r"^send_otp/", views.Generate_Otp.as_view(), name='Generate_Otp'),
    url(r"^login/", views.Login.as_view(), name='Otp_verify'),
    url(r"^forget/", views.Forget_password.as_view(), name='Forget_password'),
    url(r"^reset/", views.Reset_password.as_view(), name='Reset_password'),
    # Project Mail send Api
    url(r"^project_mail/", views.Project_Generate_Otp.as_view(), name='Project_Generate_Otp'),
    # Project APi
    url(r"^add_project/", views.Add_Project.as_view(), name='Add_Project'),
    url(r"^projects/", views.Get_All_Projects.as_view(), name='Get_All_Projects'),
    url(r"^delete_project/", views.Delete_Project.as_view(), name='Delete_Project'),
    url(r"^project_details/", views.Edit_Project.as_view(), name='Edit_Project'),
    # Plants api
    url(r"^add_plant/", views.Add_Plant.as_view(), name='Add_Plant'),

    url(r"^get_plant/", views.Get_Plant.as_view(), name='Add_Plant'),
    url(r"^get_sub_plant/", views.Get_Sub_Plant.as_view(), name='Get_Sub_Plant'),
]
