from django.contrib import admin

# Register your models here.
from .models import Review,ClinicReg,TimeRange,Saturday,Sunday,Monday,Tuesday,Wednesday,Thursday,Friday


admin.site.register(ClinicReg)
admin.site.register(Review)

admin.site.register(TimeRange)
admin.site.register(Saturday)
admin.site.register(Sunday)
admin.site.register(Monday)
admin.site.register(Wednesday)
admin.site.register(Thursday)
admin.site.register(Friday)
