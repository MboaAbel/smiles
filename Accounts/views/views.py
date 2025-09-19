from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from Accounts.forms import UserProfileUpdateForm, UserUpdateForm, RegistrationForm, LoginForm, UserPasswordResetForm, UserSetPasswordForm, \
    UserPasswordChangeForm,ReviewForm
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.contrib.auth import logout
from Accounts.models import User,Profile
from Clinic.models import Page
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from slots.models import Service, Appointment, AppointmentRequest
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from utils.htmx import render_toast_message_for_api
from Dashboard.models import ClinicReg
from doctors.models import Review
from bookings.models import Prescription
from django.db.models import Q
from django.urls import reverse_lazy
from mixins.custom_mixins import PatientRequiredMixin
from django.views.generic import UpdateView, DetailView, View, CreateView


# Create your views here.

def index(request):
    return render(request, 'account/signup.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
#            print("Account created successfully!")
            messages.success(request, 'Account created Successfully,')
            return redirect('/accounts/login/')
        else:
            print("Registration failed!")
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'account/signup.html', context)


class UserLoginView(LoginView):
    template_name = 'account/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('user_profile')  # or your target page


class UserPasswordResetView(PasswordResetView):
    template_name = 'account/includes/password_reset.html'
    form_class = UserPasswordResetForm


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'account/includes/password_reset_confirm.html'
    form_class = UserSetPasswordForm


class UserPasswordChangeView(PasswordChangeView):
    template_name = 'account/includes/password_change.html'
    form_class = UserPasswordChangeForm


def user_logout_view(request):
    logout(request)
    return render(request, 'account/includes/logged_out.html')


def user_profile_view(request):
    user_view = request.user
    page = Page.objects.all()
    Services = Service.objects.all()
    context = {'services': Services, 'page': page}
    Appointment_History = AppointmentRequest.objects.filter(email__icontains=user_view) | AppointmentRequest.objects.filter(
        mobile_number__icontains=user_view)
    if Appointment_History:
        # Filter records where fullname or Appointment Number contains the query
        Appointee = Appointment_History
        messages.info(request, 'Your Appointment History Exists')
        context = {'Appointee': Appointee, 'user_view': user_view, 'page': page, 'services': Services, }
        return render(request, 'user_profile/includes/user_profile.html', context)
    return render(request, 'user_profile/includes/user_profile.html', context)



@login_required(login_url='/accounts/login')
def user_profile(request):
    user_view = request.user
    services = Service.objects.all()
    doctor = User.objects.filter(email=user_view,user_role=User.RoleChoices.DOCTOR)

    # Get appointments based on user type
    if user_view.is_staff:
        appointments = (AppointmentRequest.objects
        .filter(status = "Pending"))
        Bookings = Prescription.objects.all()
        doctors = ClinicReg.objects.all()
        context = {
        'user_view': doctor,
        'appointments': appointments,
        'doctors':doctors,
        'bookings':Bookings,
    }
        return render(request, 'bookings/booking.html', context)

    else:
        appointments = AppointmentRequest.objects.filter(
            Q(email=user_view.email) |
            Q(mobile_number=user_view.mobile_number) |
            Q(fullname=user_view.get_full_name)
        ).order_by('-created_at')

    context = {
        'user_view': user_view,
        'services': services,
        'appointments': appointments,
        'doctor':doctor,
    }

    if appointments.exists():
        return render(request, 'dashboard/includes/profile.html', context)
    else:
        messages.info(request, 'No Appointment History Found')
        return render(request, 'user_profile/includes/profile.html', context)




class UpdateBasicUserInformation(UpdateView):
    template_name = 'user_profile/includes/user_account_update.html'
    form_class = UserUpdateForm
    model = User
    success_url = reverse_lazy("update-profile-information")



    def get_object(self, queryset=None):
        return self.request.user

           #PatientRequiredMixin,

    def form_valid(self, form):
         user_basic_info = form.save(commit=False)


         profile_fields = [
             'first_name',
             'last_name',
             'username',
             'profile_photo',
             'email',
             'mobile_number',
             'national_id',
             'next_of_kin',
             'member_code',
                     ]

         for field in profile_fields:
                  value = self.request.POST.get(field)
                  if value:
                      setattr(user_basic_info, field, value)
                      user_basic_info.save()

         messages.success(self.request, "Account updated successfully")
         return redirect(self.success_url)



    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PatientProfileUpdateView(CreateView):
    model = Profile
    template_name = 'user_profile/includes/update_profile.html'
    success_url = reverse_lazy("user_profile")
    form_class = UserProfileUpdateForm

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        profile = form.save(commit=False)


        # Update profile fields
        profile_fields = [
            "blood_group",
            "gender",
            "medical_conditions",
            "allergies",
            "address",
            "city",
            "state",
            "postal_code",
            "country",
        ]

        for field in profile_fields:
            value = self.request.POST.get(field)
            if value:
                setattr(profile, field, value)
                profile.save()

        messages.success(self.request, "Profile updated successfully")
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



class AddReviewView(PatientRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "patients/add_review.html"

    def form_valid(self, form):
        booking_id = self.kwargs.get("booking_id")
        booking = get_object_or_404(
            Prescription, id=booking_id, patient=self.request.user
        )

        if booking.status != "completed":
            messages.error(
                self.request, "You can only review completed appointments."
            )
            return redirect("patients:appointment-detail", pk=booking_id)

        if Review.objects.filter(booking=booking).exists():
            messages.error(
                self.request, "You have already reviewed this appointment."
            )
            return redirect("patients:appointment-detail", pk=booking_id)

        form.instance.patient = self.request.user
        form.instance.doctor = booking.doctor
        form.instance.booking = booking
        messages.success(self.request, "Thank you for your review!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "patients:appointment-detail",
            kwargs={"pk": self.kwargs["booking_id"]},
        )



