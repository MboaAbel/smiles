from django.contrib import admin
from .models import Prescription

admin.site.register(Prescription)

class PrescriptionAdmin(admin.ModelAdmin):


    list_display = ['booking', 'clinic','doctor','notes', 'created_at']

    def get_patient_name(self, obj):
        return obj.appointment_ok.fullname  # Assuming 'name' is a field on Appointment

    get_patient_name.short_description = 'Patient Name'
    readonly_fields = ('patient_name',)

