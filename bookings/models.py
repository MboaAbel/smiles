from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField
from Accounts.models import User
from slots.models import Appointment,StaffMember
from Dashboard.models import ClinicReg


# Helps manage bookings after vlient visits,pays,and revisits
class Prescription(models.Model):
     booking = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="booking_prescription",limit_choices_to={"status": "Approved"},
     )
     doctor = models.ForeignKey(
         StaffMember,
         on_delete=models.CASCADE,
         related_name="booking_prescriptions_given",
     )
     patient = models.ForeignKey(User,
         on_delete=models.CASCADE,
         related_name="booking_prescriptions_received",
     )
     clinic = models.ForeignKey(ClinicReg,on_delete=models.CASCADE,related_name="booking_clinic",limit_choices_to={"registered":True})
     symptoms = RichTextField(null=True,blank=True)
     diagnosis = RichTextField(null=True,blank=True)
     medications = RichTextField(null=True,blank=True)
     notes = RichTextField(blank=True)
     booking_status = models.CharField(max_length=50, null=True,blank=True)
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)

     def __str__(self):
         return f"Prescription for {self.patient} by Dr. {self.doctor}"

     class Meta:
         ordering = ["-created_at"]
         unique_together = ["doctor","booking", "patient", "clinic"]
