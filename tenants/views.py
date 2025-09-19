from django.shortcuts import render
from .models import Client, Domain

     # create  public tenant
    tenant = Client(schema_name='tenant1',
                    name='My First Tenant',
                    paid_until='2026-12-05',
                    on_trial=True)
    tenant.save()

    # Add one or more domains for the tenant
    domain = Domain()
    domain.domain = 'tenant.smileslot.onrender.com'
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()
