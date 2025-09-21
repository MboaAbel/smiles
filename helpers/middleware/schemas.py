from django.apps import apps
from django.core.cache import cache
from django.conf import settings

from helpers.db.schemas import use_public_schema, activate_tenent_schema


class SchemaTenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        host_portless = host.split(":")[0].lower()
        # Decide "subdomain candidate" (first label) for backwards compatibility
        subdomain_candidate = host_portless.split(".", 1)[0] if "." in host_portless else None

        schema_name, tenant_active = self.get_schema_name(hostname=host_portless, subdomain=subdomain_candidate)

        try:
            activate_tenent_schema(schema_name)
        except Exception as e:
            print(f"[SchemaTenantMiddleware] activate_tenent_schema({schema_name}) failed: {e}")

        request.tenant_active = tenant_active
        request.tenant_schema = schema_name
        return self.get_response(request)

    def get_schema_name(self, hostname: str, subdomain: str | None = None):
        """
        Return (schema_name, tenant_active_bool).
        Lookup strategy:
          1) If hostname is public (localhost/127.0.0.1) => public
          2) Cached (by full hostname)
          3) In public schema:
             a) If Tenant model has 'subdomain' field -> Tenant.objects.get(subdomain=subdomain)
             b) Else try to find Domain model or Tenant.domains relation matching full hostname
        """
        # 1) public hosts
        if hostname in ("localhost", "127.0.0.1"):
            return "public", False

        cache_key = f"subdomain_schema:{hostname}"
        cache_valid_key = f"subdomain_valid_schema:{hostname}"
        cached_schema = cache.get(cache_key)
        cached_valid = cache.get(cache_valid_key)
        if cached_schema is not None and cached_valid is not None:
            return cached_schema, bool(cached_valid)

        schema_name = "public"
        tenant_active = False

        with use_public_schema():
            TenantModel = None
            tried_labels = []
            # candidate app labels to look for models in
            candidate_labels = [
                getattr(settings, "TENANTS_APP_LABEL", None),
                "clinic",
                "Clinic",
                "tenants",
            ]
            # uniquify
            candidate_labels = [l for i, l in enumerate(candidate_labels) if l and l not in candidate_labels[:i]]

            # find Tenant model
            for label in candidate_labels:
                try:
                    TenantModel = apps.get_model(label, "Tenant")
                    tenant_app_label = label
                    break
                except LookupError:
                    tried_labels.append(label)
                    TenantModel = None

            if TenantModel is None:
                print("[SchemaTenantMiddleware] Tenant model not found. Tried labels:", tried_labels)
            else:
                # Inspect fields to know whether 'subdomain' exists
                field_names = [f.name for f in TenantModel._meta.get_fields()]

                # Strategy A: Tenant has a 'subdomain' field
                if "subdomain" in field_names and subdomain:
                    try:
                        obj = TenantModel.objects.get(subdomain=subdomain)
                        schema_name = obj.schema_name
                        tenant_active = True
                    except TenantModel.DoesNotExist:
                        print(f"[SchemaTenantMiddleware] no Tenant with subdomain='{subdomain}'")
                    except Exception as e:
                        print(f"[SchemaTenantMiddleware] error fetching Tenant by subdomain: {e}")

                # Strategy B: Try Domain model lookup (full hostname)
                if not tenant_active:
                    DomainModel = None
                    try:
                        # First try domain model inside same app
                        DomainModel = apps.get_model(tenant_app_label, "Domain")
                    except LookupError:
                        # try a few common alternative labels
                        for alt_label in ("tenants", "domains", "clinic", "Clinic"):
                            try:
                                DomainModel = apps.get_model(alt_label, "Domain")
                                break
                            except LookupError:
                                DomainModel = None

                    if DomainModel is not None:
                        # try to find Domain record matching the full hostname
                        try:
                            # assume Domain has a 'domain' field and FK to tenant named 'tenant' or similar;
                            domain_obj = DomainModel.objects.filter(domain__iexact=hostname).first()
                            if domain_obj:
                                # if Domain points directly to Tenant via a 'tenant' FK
                                tenant_candidate = getattr(domain_obj, "tenant", None)
                                if tenant_candidate is not None:
                                    schema_name = tenant_candidate.schema_name
                                    tenant_active = True
                                else:
                                    # Maybe Domain is reverse-related via 'domains' on Tenant
                                    # Try finding tenant via TenantModel relation
                                    t = TenantModel.objects.filter(domains__domain__iexact=hostname).first()
                                    if t:
                                        schema_name = t.schema_name
                                        tenant_active = True
                        except Exception as e:
                            print(f"[SchemaTenantMiddleware] error looking up Domain for '{hostname}': {e}")
                    else:
                        # As last resort, try TenantModel relation 'domains' directly
                        if "domains" in field_names:
                            try:
                                t = TenantModel.objects.filter(domains__domain__iexact=hostname).first()
                                if t:
                                    schema_name = t.schema_name
                                    tenant_active = True
                            except Exception as e:
                                print(f"[SchemaTenantMiddleware] error querying Tenant.domains for '{hostname}': {e}")

        # cache results (short TTL)
        cache_ttl = getattr(settings, "TENANT_CACHE_TTL", 60)
        cache.set(cache_key, schema_name, cache_ttl)
        cache.set(cache_valid_key, tenant_active, cache_ttl)

        return schema_name, tenant_active
