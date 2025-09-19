from django.urls import path
from .views import views
from django.contrib.auth import views as auth_views
from .views.views import AddReviewView
from .views.auth import LoginAPIView, PersonalRegistrationView
from rules.urldecorators import include, re_path
from django.conf.urls.static import static
from django.conf import settings
from saas.compat import reverse_lazy

urlpatterns = [
    # Authentication
    path('update_info', views.UpdateBasicUserInformation.as_view(), name='update-basic-information'),
    path('update_profile/',views.PatientProfileUpdateView.as_view(),name="update-profile-information",),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/view', views.user_profile_view, name='user_profile_view'),
    path("appointment/<int:booking_id>/review/",AddReviewView.as_view(),name="add-review",),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.user_logout_view, name='logout'),
    path('signup/', views.register, name='register'),
    path('password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/includes/password_change_done.html'
    ), name="password_change_done"),
    path('password-reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/includes/password_reset_done.html'
    ), name='password_reset_done'),
    path('includes/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/includes/password_reset_complete.html'
    ), name='password_reset_complete'),
]

def url_prefixed(regex, view, name=None, redirects=None):
    return re_path(r'^' + regex, view, name=name, redirects=redirects)

urlpatterns += \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    url_prefixed(r'api/auth', LoginAPIView.as_view(), name='api_login'),
    url_prefixed(r'register/$',PersonalRegistrationView.as_view(
             success_url=reverse_lazy('home')),name='registration_register'),

]
