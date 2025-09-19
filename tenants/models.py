from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Tenant(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField()
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)

    # Dental-specific fields
    clinic_name = models.CharField(max_length=200)
    clinic_owner_name = models.CharField(max_length=200)
    subscription_plan = models.CharField(max_length=50, default='basic')
    max_users = models.IntegerField(default=5)
    max_patients = models.IntegerField(default=500)

    auto_create_schema = True

class Domain(DomainMixin):
    pass

# Create your models here.
