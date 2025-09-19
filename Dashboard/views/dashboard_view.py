from Accounts.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from Dashboard.models import ClinicReg
from bookings.models import Prescription
from slots.models import Appointment,AppointmentRequest, Service, StaffMember
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
from Clinic.models import Page
from mixins.custom_mixins import DoctorRequiredMixin
from django.db.models import Q
from django.views.generic import UpdateView, DetailView, View

# Create your views here.


@login_required(login_url='/accounts/login')
def DoctorSignup(request):
    specialization = Specialization.objects.all()
    if request.method == "POST":
        profile_photo = request.FILES.get('pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        mobno = request.POST.get('mobno')
        specialization_id = request.POST.get('specialization_id')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.warning(request, 'Email already exist')
            return redirect('dashboard:Doctor_registration')
        if User.objects.filter(username=username).exists():
            messages.warning(request, 'Username already exist')
            return redirect('dashboard:Doctor_registration')
        else:
            user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                role="doctor",
                profile_photo=profile_photo,
            )
            user.set_password(password)
            user.save()
            spid = Specialization.objects.get(id=specialization_id)
            doctor = ClinicReg(
                member=user,
                mobile_number=mobno,
                clinic_specializations=spid,

            )
            doctor.save()
            messages.success(request, 'Signup Successfully')
            return redirect('login')

    context = {
        'specialization': specialization
    }

    return render(request, 'dashboard/includes/docreg.html', context)

@login_required(login_url='/accounts/login')
def create_appointment(request):
    clinic_view = (ClinicReg.objects
        .select_related("member"))
        #.filter(role="doctor"
        # .filter(is_superuser=True)
    worry = Specialization.objects.all()
    page = Page.objects.all()

    if request.method == "POST":
        appointment_number = random.randint(100000000, 999999999)
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        date_of_appointment = request.POST.get('date_of_appointment')
        time_of_appointment = request.POST.get('time_of_appointment')
        clinic_id = request.POST.get('clinic_id')
        worry_id = request.POST.get('worry_need')
        additional_msg = request.POST.get('additional_msg')

        # Retrieve the DoctorReg instance using the doctor_id
        clinic_instance = ClinicReg.objects.get(slug=clinic_id)
        worry_instance = Specialization.objects.get(id=worry_id)

        # Validate that *date_of_appointment is greater than today's date
        try:
            appointment_date = datetime.strptime(date_of_appointment, '%Y-%m-%d').date()
            today_date = datetime.now().date()

            if appointment_date <= today_date:
                # If the appointment date is not in the future, display an error message
                messages.error(request, "Please select a date in the future for your appointment")
                return redirect('appointment')  # Redirect back to the appointment page
        except ValueError:
            # Handle invalid date format error
            messages.error(request, "Invalid date format")
            return redirect('appointment')  # Redirect back to the appointment page

        # Create a new Appointment instance with the provided data
        appointment_details = Appointment.objects.create(
            appointment_number=appointment_number,
            fullname=full_name,
            email=email,
            mobile_number=mobile_number,
            date_of_appointment=date_of_appointment,
            time_of_appointment=time_of_appointment,
            clinic=clinic_instance,
            worry_id=worry_instance,
            additional_msg=additional_msg
        )

        if User.objects.filter(email=email).exists() | User.objects.filter(username=full_name).exists():
            messages.info(request, 'Account exist on Membership Plan . Kindly Login to your Account')
        # Display a success message
        messages.success(request, "Your Appointment Request Has Been Sent. We Will Contact You Soon")
        appointment_details.save()
        context = {'clinic_view': clinic_view,'clinic':clinic, 'appointment_details': appointment_details,
                   'page': page}
        return render(request, 'accounts/includes/appointment_success.html', context)

    context = {'clinic': clinic_view, 'worry': worry,
               'page': page}
    return render(request, 'dashboard/includes/appointment.html', context)


@login_required(login_url='/accounts/login')
def Dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')


@login_required(login_url='/accounts/login')
def View_Appointment(request):
    try:
        doctor_admin = request.user
        doctor_reg = ClinicReg.objects.get(admin=doctor_admin)
        view_appointment = Appointment.objects.filter(clinic_id=doctor_reg)

        # Pagination
        paginator = Paginator(view_appointment, 5)  # Show 10 appointments per page
        page = request.GET.get('page')
        try:
            view_appointment = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            view_appointment = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            view_appointment = paginator.page(paginator.num_pages)

        context = {'view_appointment': view_appointment}
    except Exception as e:
        # Handle exceptions, such as database errors, gracefully
        context = {'error_message': str(e)}

    return render(request, 'dashboard/includes/view_appointment.html', context)

@login_required(login_url='/accounts/login')
def Search_Appointments(request):
    doctor_admin = request.user
    doctor_reg = ClinicReg.objects.get(member=doctor_admin)
    if request.method == "GET":
        query = request.GET.get('query', '')
        if query:
            # Filter records where fullname or Appointment Number contains the query
            patient = Appointment.objects.filter(fullname__icontains=query) | Appointment.objects.filter(
                appointment_number__icontains=query) & Appointment.objects.filter(clinic_id=doctor_reg)
            messages.success(request, "Search against " + query)
            return render(request, 'dashboard/includes/search-appointment.html', {'patient': patient, 'query': query})
        else:
            print("No Record Found")
            return render(request, 'dashboard/includes/search-appointment.html', {})


@login_required(login_url='/accounts/login')
def Between_Date_Report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    patient = []
    doctor_admin = request.user
    doctor_reg = ClinicReg.objects.get(member=doctor_admin)

    if start_date and end_date:
        # Validate the date inputs
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'dashboard/includes/between-dates-report.html',
                          {'visitor': patient, 'error_message': 'Invalid date format'})

        # Filter Appointment between the given date range
        patient = Appointment.objects.filter(created_at__range=(start_date, end_date)) & Appointment.objects.filter(
            clinic_id=doctor_reg)

    return render(request, 'dashboard/includes/between-dates-report.html',
                  {'patient': patient, 'start_date': start_date, 'end_date': end_date})

@login_required(login_url='/accounts/login')
def Patient_Appointment_Prescription(request):
    if request.method == 'POST':
        patient_id = request.POST.get('pat_id')
        prescription = request.POST['prescription']
        recommendedtest = request.POST['recommendedtest']
        status = request.POST['status']
        patientaptdet = Appointment.objects.get(id=patient_id)
        patientaptdet.prescription = prescription
        patientaptdet.recommendedtest = recommendedtest
        patientaptdet.status = status
        patientaptdet.save()
        messages.success(request, "Status Update successfully")
        context = {'patients': patientaptdet}
        return render(request, 'dashboard/includes/patient_list_app_appointment.html', context)
    return render(request, 'dashboard/includes/patient_appointment_details.html',)



@login_required(login_url='/accounts/login')
def Patient_Appointment_Completed(request):
    doctor_admin = request.user
    doctor_reg = ClinicReg.objects.get(member=doctor_admin)
    patientdetails1 = Appointment.objects.filter(status='Completed', clinic_id=doctor_reg)
    context = {'patientdetails1': patientdetails1, 'app_word': 'Completed'}
    return render(request, 'dashboard/includes/patient_list_app_appointment.html', context)




class AppointmentDetailView(DoctorRequiredMixin, DetailView):
    model = Prescription
    template_name = "dashboard/includes/patient_appointment_details.html"
    context_object_name = "appointment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.object.patient

        # Get patient's appointment history with this doctor
        context["patient_history"] = (
            Prescription.objects.select_related("doctor", "doctor__profile")
            .filter(
                doctor=self.request.user,
                patient=patient,
                appointment_date__lt=self.object.appointment_date,
            )
            .order_by("-appointment_date", "-appointment_time")
        )

        # Get total visits count
        context["total_visits"] = Prescription.objects.filter(
            doctor=self.request.user, patient=patient, status="completed"
        ).count()

        return context




@login_required(login_url='/accounts/login')
def Patient_Appointment_Details(request, id, appointment_number):
    patientdetails = AppointmentRequest.objects.filter(id=id,appointment_number=appointment_number)
    context = {'patientdetails': patientdetails, 'app_word': appointment_number}

    return render(request, 'dashboard/includes/patient_appointment_details.html', context)


@login_required(login_url='/accounts/login')
def Patient_Appointment_Details_Remark(request):
    if request.method == 'POST':
        patient_id = request.POST.get('pat_id')
        remark = request.POST['remark']
        status = request.POST['status']
        patientaptdet = Appointment.objects.get(id=patient_id,)
        patientaptdet.remark = remark
        patientaptdet.status = status
        patientaptdet.save()
        messages.success(request, "Status Update successfully")
        context = {'UpApp': patientaptdet, 'app_word':'Updated'}
        return render(request, 'dashboard/includes/doctor_appointment_list_details.html', context)

    return redirect('view_appointment')

@login_required(login_url='/accounts/login')
def Patient_Approved_Appointment(request):
    doctor_admin = request.user
    doctor_reg = ClinicReg.objects.get(member=doctor_admin)
    patientdetails1 = Appointment.objects.filter(status='Approved', clinic_id=doctor_reg)
    context = {'patientdetails1': patientdetails1, 'app_word': 'Approved'}
    return render(request, 'dashboard/includes/patient_app_appointment.html', context)

@login_required(login_url='/accounts/login')
def Patient_Cancelled_Appointment(request):
    doctor_admin = request.user
    doctor_reg = ClinicReg.objects.get(member=doctor_admin)
    patientdetails1 = Appointment.objects.filter(status='Cancelled', clinic_id=doctor_reg)
    context = {'patientdetails1': patientdetails1, 'app_word': 'Cancelled'}
    return render(request, 'dashboard/includes/patient_app_appointment.html', context)


@login_required(login_url='/accounts/login')
def Patient_New_Appointment(request):
    doctor_admin = request.user
    doctor_reg = ClinicReg.objects.get(member=doctor_admin)
    patientdetails1 = Appointment.objects.filter(status='0', clinic_id=doctor_reg)
    context = {'patientdetails1': patientdetails1, 'app_word': 'New'}
    return render(request, 'dashboard/includes/patient_app_appointment.html', context)

@login_required(login_url='/accounts/login')
def Patient_List_Approved_Appointment(request):
    doctor_admin = request.user
    doctor_reg = ClinicReg.objects.get(member=doctor_admin)
    patientdetails1 = Appointment.objects.filter(status='Approved', clinic_id=doctor_reg)
    context = {'patientdetails1': patientdetails1, 'app_word': 'Approved'}
    return render(request, 'dashboard/includes/patient_list_app_appointment.html', context)


@login_required(login_url='/accounts/login')
def DoctorAppointmentList(request, id):
    patientdetails = Appointment.objects.filter(id=id,status='Completed')
    context = {'patientdetails': patientdetails, 'app_word': 'Doctor Approved List '

               }
    return render(request, 'dashboard/includes/doctor_appointment_list_details.html', context)


@login_required(login_url='/accounts/login')
def mpesa(request):
    return render(request, 'dashboard/includes/billing.html')


@login_required(login_url='/accounts/login')
def records(request):
    return render(request, 'dashboard/includes/tables.html')


@login_required(login_url='/accounts/login')
def member(request):
    return render(request, 'dashboard/includes/profile.html')
