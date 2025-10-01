from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from .models import  Page, Blog
from slots.models import Service, Appointment
from Dashboard.models import ClinicReg
from datetime import datetime
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse
from django.http import JsonResponse
from .utils import send_sms
from django.shortcuts import render, redirect
from urllib.parse import urlencode
from Accounts.models import User
from django.views.generic import (ListView,DetailView,View,CreateView, )
from doctors.models.general import *
from .forms import BlogForm
import math
from django.db import connection
from django.views.decorators.http import require_GET

EARTH_KM = 6371.0

def haversine(lat1, lon1, lat2, lon2):
    # returns distance in km
    # using radians arithmetic - (we won't use it in SQL version below)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return EARTH_KM * c

@require_GET
def nearby_clinics_haversine(request):
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
    except (TypeError, ValueError):
        return JsonResponse({"error": "lat and lng required"}, status=400)

    radius_km = float(request.GET.get('radius_km', 5.0))
    limit = int(request.GET.get('limit', 50))

    # Efficient prefilter: compute bounding box to reduce rows scanned
    # approximate lat/lng delta for radius
    lat_delta = radius_km / 111.0  # ~111 km per degree lat
    lng_delta = radius_km / max(0.00001, (111.320 * math.cos(math.radians(lat))))

    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    min_lng = lng - lng_delta
    max_lng = lng + lng_delta

    sql = """
    SELECT id, name, lat, lng, address
    FROM clinics_clinic
    WHERE lat BETWEEN %s AND %s AND lng BETWEEN %s AND %s
    LIMIT 1000;
    """
    params = [min_lat, max_lat, min_lng, max_lng]
    with connection.cursor() as c:
        c.execute(sql, params)
        rows = c.fetchall()

    clinics = []
    for r in rows:
        cid, name, plat, plng, addr = r
        if plat is None or plng is None:
            continue
        dist = haversine(lat, lng, plat, plng)
        if dist <= radius_km:
            clinics.append({
                "id": cid,
                "name": name,
                "address": addr or "",
                "lat": plat,
                "lng": plng,
                "distance_km": round(dist, 2),
                # top_services: fetch top 3 services by price or popularity (simple example)
                "top_services": []  # fill below
            })

    # fetch top_services for these clinic ids in one query
    clinic_ids = [c["id"] for c in clinics]
    if clinic_ids:
        placeholders = ",".join(["%s"] * len(clinic_ids))
        svc_sql = f"""
        SELECT id, clinic_id, name, duration_mins, price
        FROM clinics_service
        WHERE clinic_id IN ({placeholders})
        ORDER BY clinic_id, id
        """
        with connection.cursor() as c:
            c.execute(svc_sql, clinic_ids)
            svc_rows = c.fetchall()
        svc_by_clinic = {}
        for sid, cid, sname, sdur, sprice in svc_rows:
            svc_by_clinic.setdefault(cid, []).append({
                "id": sid, "name": sname, "duration_mins": sdur, "price": float(sprice) if sprice is not None else None
            })
        for cl in clinics:
            cl["top_services"] = svc_by_clinic.get(cl["id"], [])[:3]

    # sort by distance
    clinics.sort(key=lambda x: x["distance_km"])
    # limit
    clinics = clinics[:limit]

    return JsonResponse(clinics, safe=False)



def health_check(request):
    return HttpResponse("OK", status=200)

days = {
     0: Sunday,
     1: Monday,
     2: Tuesday,
     3: Wednesday,
     4: Thursday,
     5: Friday,
     6: Saturday,
 }




class ClinicProfileView(DetailView):
     context_object_name = "clinic"
     model = ClinicReg
     slug_url_kwarg = "clinic_code"
     slug_field = "clinic_code"
     template_name = "clinic/profile.html"

     def get_object(self, queryset=None):
         if queryset is None:
             queryset = self.get_queryset()

         slug = self.kwargs.get(self.slug_url_kwarg)
         queryset = queryset.select_related("member").prefetch_related(
             "member",
             "sunday__time_range",
             "monday__time_range",
             "tuesday__time_range",
             "wednesday__time_range",
             "thursday__time_range",
             "friday__time_range",
             "saturday__time_range",
         )

         try:
             obj = queryset.get(
                 **{self.slug_field: slug}
             )
         except ClinicReg.DoesNotExist:
             return render(self.request, 'clinic/includes/new_clinic.html',)

         return obj

     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         clinic = self.object

         # Get current day name
         current_day = datetime.now().strftime("%A")

         # Prepare business hours
         business_hours = {
             "Sunday": (
                 clinic.sunday.time_range.all()
                 if hasattr(clinic, "sunday")
                 else []
             ),
             "Monday": (
                 clinic.monday.time_range.all()
                 if hasattr(clinic, "monday")
                 else []
             ),
             "Tuesday": (
                 clinic.tuesday.time_range.all()
                 if hasattr(clinic, "tuesday")
                 else []
             ),
             "Wednesday": (
                 clinic.wednesday.time_range.all()
                 if hasattr(clinic, "wednesday")
                 else []
             ),
             "Thursday": (
                 clinic.thursday.time_range.all()
                 if hasattr(clinic, "thursday")
                 else []
             ),
             "Friday": (
                 clinic.friday.time_range.all()
                 if hasattr(clinic, "friday")
                 else []
             ),
             "Saturday": (
                 clinic.saturday.time_range.all()
                 if hasattr(clinic, "saturday")
                 else []
             ),
         }
         context.update(
             {
                 "current_day": current_day,
                 "business_hours": business_hours,
                 #"staff": clinic.clinic_staff.select_related(
                   #   "doctors", "doctors__profile"
                  #).order_by("-date_joined"),
             }
         )

         return context


def generate_whatsapp_link(request):
    phone_number = "254708534184"
    base_url = f"https://wa.me/{phone_number}"
    message = "Hello! I'd like to book an appointment for dental services."
    encoded_message = urlencode({'text': message})
    whatsapp_url = f"{base_url}?{encoded_message}"

    return render(request, 'template_name.html', {'whatsapp_url': whatsapp_url})


@login_required(login_url='/Accounts/login')
def doctor_home(request):
    doctor_count = ClinicReg.objects.all().count
    context = {
        'doctor_count': doctor_count,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required(login_url='/Accounts/login')
def Specialization(request):
    if request.method == "POST":
        specializationname = request.POST.get('specializationname')
        specialization = Specialization(
            sname=specializationname,
        )
        specialization.save()
        messages.success(request, 'Specialization  Added Succeesfully!!!')
        return redirect("add_specilizations")
    return render(request, 'admin/specialization.html')

@login_required(login_url='/Accounts/login')
def Manage_Specialization(request):
    specialization = Specialization.objects.all()
    context = {'specialization': specialization,

               }
    return render(request, 'admin/manage_specialization.html', context)


def Delete_Specialization(request, id):
    specialization = Specialization.objects.get(id=id)
    specialization.delete()
    messages.success(request, 'Record Delete Succeesfully!!!')

    return redirect('manage_specilizations')


@login_required(login_url='/Accounts/login')


def Update_Specialization(request, id):
    specialization = Specialization.objects.get(id=id)

    context = {
        'specialization': specialization,
    }

    return render(request, 'admin/update_specialization.html', context)


@login_required(login_url='/Accounts/login')


def Update_Specialization_Details(request):
    if request.method == 'POST':
        sep_id = request.POST.get('sep_id')
        sname = request.POST.get('sname')
        sepcialization = Specialization.objects.get(id=sep_id)
        sepcialization.sname = sname
        sepcialization.save()
        messages.success(request, "Your specialization detail has been updated successfully")
        return redirect('manage_specilizations')
    return render(request, 'admin/update_specialization.html')


@login_required(login_url='/Accounts/login')
def DoctorList(request):
    doctorlist = DoctorReg.objects.all()
    context = {'doctorlist': doctorlist,

               }
    return render(request, 'admin/doctor-list.html', context)


def ViewDoctorDetails(request, id):
    doctorlist1 = DoctorReg.objects.filter(id=id)
    context = {'doctorlist1': doctorlist1

               }

    return render(request, 'admin/doctor-details.html', context)


def ViewDoctorAppointmentList(request, id):
    patientdetails = Appointment.objects.filter(doctor_id=id)
    context = {'patientdetails': patientdetails

               }

    return render(request, 'admin/doctor_appointment_list.html', context)


def ViewPatientDetails(request, id):
    patientdetails = Appointment.objects.filter(id=id)
    context = {'patientdetails': patientdetails

               }

    return render(request, 'admin/patient_appointment_details.html', context)


def Search_Doctor(request):
    if request.method == "GET":
        query = request.GET.get('query', '')
        if query:
            # Filter records where email or mobilenumber contains the query
            searchdoc = DoctorReg.objects.filter(mobilenumber__icontains=query) | DoctorReg.objects.filter(
                admin__first_name__icontains=query) | DoctorReg.objects.filter(admin__last_name__icontains=query)
            messages.info(request, "Search against " + query)
            return render(request, 'admin/search-doctor.html', {'searchdoc': searchdoc, 'query': query})
        else:
            print("No Record Found")
            return render(request, 'admin/search-doctor.html', {})


def Doctor_Between_Date_Report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    doctor = []

    if start_date and end_date:
        # Validate the date inputs
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'admin/doctor-between-date.html',
                          {'doctor': doctor, 'error_message': 'Invalid date format'})

        # Filter visitors between the given date range
        doctor = DoctorReg.objects.filter(regdate_at__range=(start_date, end_date))

    return render(request, 'admin/doctor-between-date.html',
                  {'doctor': doctor, 'start_date': start_date, 'end_date': end_date})


def HeroView(request):
    doctors = User.objects.filter(user_role=User.RoleChoices.DOCTOR)
    blog = Blog.objects.all()

    return render(request, "clinic/index.html",{'blog':blog,'doctors':doctors})





def blog_page(request):
     doctors = User.objects.filter(user_role=User.RoleChoices.DOCTOR)
     blog = Blog.objects.all()
     return render(request, "clinic/includes/blog_page.html",{'blog':blog,'doctors':doctors})



@login_required(login_url='accounts/login')
def blog_post(request):
    form = BlogForm()
    soshi_user = request.user.username
    if request.method == 'POST':
         caption = request.POST['caption']
         blog_title = request.POST['blog_title']
         blog_subtitle = request.POST['blog_subtitle']
         blog_image = request.POST['blog_image']
         new_post = Blog.objects.create(blog_image=blog_image, blog_title=blog_title,blog_subtitle=blog_subtitle,
               caption=caption,soshi_user=soshi_user)
         new_post.save()
         return render(request, "clinic/includes/blog_post.html",{'form':form})
    return redirect('/new_post')




def new_blog(request):
    form = BlogForm()
    return render(request, "clinic/includes/blog_post.html",{'form':form})



def sms_reply(request):
    response = MessagingResponse()
    response.message("Thank you for your message!")
    return HttpResponse(str(response), content_type="text/xml")


def offline(request):
    return render(request, "clinic/includes/offline.html")

def send_sms_view(request):
    to = request.GET.get('to')  # e.g., "+1234567890"
    message = request.GET.get('message', 'Hello from Twilio!')

    if not to:
        return JsonResponse({"error": "Recipient number is required."}, status=400)

    sms = send_sms(to, message)

    if sms:
        return JsonResponse({"success": f"Message sent to {to}"})
    return JsonResponse({"error": "Failed to send message."}, status=500)



    #   feed_list = list(chain(*feed))

    # # user suggestion starts
    # all_users = User.objects.all()
    # user_following_all = []

    # for user in user_following:
    #     user_list = User.objects.get(username=user.user)
    #     user_following_all.append(user_list)
    # new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    # current_user = User.objects.filter(username=request.user.username)
    # final_suggestions_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]
    # random.shuffle(final_suggestions_list)

    #    username_profile = []
    # username_profile_list = []

    # for users in final_suggestions_list:
    #     username_profile.append(users.id)

    # for ids in username_profile:
    #     profile_lists = Profile.objects.filter(id_user=ids)
    #     username_profile_list.append(profile_lists)

    # suggestions_username_profile_list = list(chain(*username_profile_list))


    # return render(request, 'index.html', {'user_profile': user_profile, 'posts':feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})





def clinic_list(request):
    doctor_list = ClinicReg.objects.all()
    context = {'clinics':doctor_list}
    return render(request, "nav/clinic_slide.html", context)
