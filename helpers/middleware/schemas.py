from django.apps import apps
from django.core.cache import cache
from django.conf import settings

from helpers.db.schemas import (
    use_public_schema,
    activate_tenent_schema,  # keep your existing function name
)
from helpers.db import statements as db_statements


class SchemaTenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        host_portless = host.split(":")[0].lower()
        subdomain = self._extract_subdomain(host_portless)

        schema_name, tenant_active = self.get_schema_name(subdomain=subdomain)
        # activate tenant schema for the request lifecycle
        try:
            activate_tenent_schema(schema_name)
        except Exception as e:
            # if schema activation fails, log to console for dev debugging
            print(f"[SchemaTenantMiddleware] activate_tenent_schema({schema_name}) failed: {e}")

        request.tenant_active = tenant_active
        request.tenant_schema = schema_name
        return self.get_response(request)

    def _extract_subdomain(self, host):
        """
        Returns the subdomain string when host looks like <subdomain>.domain...
        Returns None for public hosts like 'localhost' or '127.0.0.1' or single-label hosts.
        Examples:
            'mboa.localhost' -> 'mboa'
            'mboa.smileslot.onrender.com' -> 'mboa'
            'localhost' -> None
            '127.0.0.1' -> None
        """
        # treat obvious public hosts as no-subdomain
        if host in ("localhost", "127.0.0.1"):
            return None

        parts = host.split(".")
        if len(parts) == 1:
            return None  # single-label host -> public
        # otherwise first label is candidate subdomain
        return parts[0]

    def get_schema_name(self, subdomain=None):
        """
        Returns (schema_name: str, tenant_active: bool).
        tenant_active == True only if we found a tenant record for subdomain.
        """
        # If no subdomain -> public site
        if subdomain is None:
            return "public", False

        cache_subdomain_key = f"subdomain_schema:{subdomain}"
        cache_subdomain_valid_key = f"subdomain_valid_schema:{subdomain}"
        cache_subdomain_val = cache.get(cache_subdomain_key)
        cache_subdomain_valid_val = cache.get(cache_subdomain_valid_key)

        if cache_subdomain_val is not None and cache_subdomain_valid_val is not None:
            # cached schema name (string) and bool
            return cache_subdomain_val, bool(cache_subdomain_valid_val)

        schema_name = "public"
        tenant_active = False

        # We need to look up tenant from the public schema
        with use_public_schema():
            TenantModel = None
            tried_labels = []
            # Try a few app labels in case your app config label differs
            candidate_labels = [
                getattr(settings, "TENANTS_APP_LABEL", None),
                "clinic",
                "Clinic",
                "tenants",
                "tenancy",
            ]
            # keep unique and remove None
            candidate_labels = [l for i, l in enumerate(candidate_labels) if l and l not in candidate_labels[:i]]
            for label in candidate_labels:
                try:
                    TenantModel = apps.get_model(label, "Tenant")
                    break
                except LookupError:
                    tried_labels.append(label)
                    TenantModel = None

            if TenantModel is None:
                # helpful debug output in dev
                print(
                    "[SchemaTenantMiddleware] Tenant model not found. Tried labels:",
                    tried_labels,
                )
            else:
                try:
                    obj = TenantModel.objects.get(subdomain=subdomain)
                    schema_name = obj.schema_name
                    tenant_active = True
                except TenantModel.DoesNotExist:
                    # no tenant with that subdomain; leave schema_name='public'
                    print(f"[SchemaTenantMiddleware] subdomain '{subdomain}' does not exist as Tenant")
                except Exception as e:
                    # unexpected DB error
                    print(f"[SchemaTenantMiddleware] error fetching Tenant for '{subdomain}': {e}")

        # cache results (short TTL during development)
        cache_ttl = getattr(settings, "TENANT_CACHE_TTL", 60)  # seconds
        cache.set(cache_subdomain_key, schema_name, cache_ttl)
        cache.set(cache_subdomain_valid_key, tenant_active, cache_ttl)

        return schema_name, tenant_active
