DEFAULT_APPS = [
      # django-apps
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',


    # third-party-apps

    #'allauth_ui',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_hosts',
    'ckeditor',
    'channels',
    'rules',
    'rest_framework',
    'africastalking',
    'django_countries',
    'phonenumber_field',
    'django_tenants',
    'django_browser_reload',
]

# tenant/enterpise apps
_CUSTOMER_INSTALLED_APPS = DEFAULT_APPS + [
    # my-apps
    'Commando',
    'Accounts',
    'Clinic',
    'mpesa',
    'patients',
    'slots',
    'saas',
    'Dashboard',
    'doctors',
    'bookings',
    'billings',
    'tenants',
    'SmileSlot',
]
# reverse("tenants:list")

# public schema default installed apps
_INSTALLED_APPS = _CUSTOMER_INSTALLED_APPS + [
    # my-apps
    'patients',
    'doctors',
    'tenants',
    'SmileSlot',
]

_INSTALLED_APPS = list(set(_INSTALLED_APPS))
#list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]
