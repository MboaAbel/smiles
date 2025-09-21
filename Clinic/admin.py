from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Tenant, Domain, Page, Blog

# Register your models here.

admin.site.register(Page)
admin.site.register(Blog)


@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'paid_until', 'on_trial')
@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')
