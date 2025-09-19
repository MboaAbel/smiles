from django.urls import path

from .views import (
    BookingView,
    BookingCreateView,
    BookingSuccessView,
    BookingInvoiceView,
    ReceptionBookingView,
    BookingListView,
)
from . import views

app_name = "bookings"

urlpatterns = [
    path(
        "doctor/<slug:username>/<str:appointment_no>/",
        BookingView.as_view(),
        name="doctor-booking-view",
    ),

    path(
        "create/<str:username>/<str:appointment_no>/",
        BookingCreateView.as_view(),
        name="create-booking-view",
    ),
    #path("save-booking/<str:appointment_no>",views.SaveBooking,name="save-booking"),
    path(
        "schedule/<str:username>",
        ReceptionBookingView.as_view(),
        name="booking-view-reception",
    ),
    path(
    "update/<str:username>/<str:appointment_no>/<str:booking_id> ",
         BookingCreateView.as_view(),
         name="booking-update",     ),
    path(
        "<int:booking_id>/success/",
        BookingSuccessView.as_view(),
        name="booking-success",
    ),
    path(
        "<int:booking_id>/invoice/",
        BookingInvoiceView.as_view(),
        name="booking-invoice",
    ),
    path(
         "list/",
         BookingListView.as_view(),
         name="booking-list",
     ),
]
