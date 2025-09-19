from django.urls import path
from .views import *



urlpatterns = [
    path('', HeroView, name='hero'),
    path('blog', blog_page, name='blog_page'),
    path('post', blog_post, name='blog_post'),
    path('new_post', new_blog, name='new_blog'),
    path('sms/', sms_reply, name='sms_reply'),
    path('offline', offline, name='offline'),
    path('clinics/', clinic_list, name='clinics'),
    path('health/', health_check, name='health-check'),
    path("clinics/<str:clinic_code>/",ClinicProfileView.as_view(),name="clinic-profile",),

]

