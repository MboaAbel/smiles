import dj_database_url
from pathlib import Path
import os
from decouple import config

from random import choice
from django.contrib.messages import constants as messages


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# Secret Key
SECRET_KEY = config('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)


ALLOWED_HOSTS = [
     '.onrender.com',
     '.localhost',
     '.sleek.work.gd',
     'sleek.work.gd'
 ]
if DEBUG:
     ALLOWED_HOSTS += [
         'localhost',
         '.localhost',
         '.onrender.com',
         '.sleek.work.gd',
         'sleek.work.gd'
     ]



APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
RUN_DIR = os.getenv('RUN_DIR', os.getcwd())
DB_NAME = os.path.join(RUN_DIR, 'db.sqlite')
LOG_FILE = os.path.join(RUN_DIR, 'billing-app.log')
FEATURES_DEBUG = True
TEMPLATE_REVERT_TO_DJANGO = True
JS_FRAMEWORK = 'vuejs'
SAAS_ORGANIZATION_MODEL = 'saas.Organization'
USE_STRIPE_V2 = True





# ----------------------------
# django-tenants app split
# ----------------------------

# APPS that live in the public schema (shared by everyone)
SHARED_APPS = (
    # required
    "django_tenants",       # must be first
    "Clinic",              # your tenant model app: Client/Domain

    # minimal django core that should be in public
    "django.contrib.contenttypes",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "ckeditor",
    "rules",
    "rest_framework",
    "phonenumber_field",
    "django_countries",
    # ...any other libs you use per-tenant...
    "SmileSlot",

    # Your project apps (tenant-specific data)
    "Commando",
    "Accounts",
    "saas",
    "mpesa",
    "slots",
    "Dashboard",
)

# APPS that live inside each tenant schema (one copy per tenant)
TENANT_APPS = (
    "patients",
    "doctors",
    "bookings",
    "billings",
)

# FINAL INSTALLED_APPS used by Django (do not duplicate)
INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

# Link to the tenant model
TENANT_MODEL = "Clinic.Tenant"            # app_label.ModelName
TENANT_DOMAIN_MODEL = "Clinic.Domain"
# ----------------------------


# Keep cookies host-specific so public and tenant sessions don't collide:
SESSION_COOKIE_DOMAIN = None
CSRF_COOKIE_DOMAIN = None

# Optional: make it easy to change tenant-app label if you have custom name
TENANTS_APP_LABEL = "Clinic"   # <-- your app label that contains Tenant model

PUBLIC_SCHEMA_NAME = 'public'
BASE_DOMAIN = 'sleek.work.gd'


SITE_ID = 1

MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django_hosts.middleware.HostsRequestMiddleware',
    'helpers.middleware.schemas.SchemaTenantMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',

]


DEFAULT_HOST = "www"
PARENT_HOST = "sleek.work.gd/"
ROOT_HOSTCONF = "SmileSlot.hosts"
ENTERPRISES_URLCONF = "SmileSlot.urls"
ROOT_URLCONF = 'SmileSlot.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR / 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ----------------------
WSGI_APPLICATION = 'SmileSlot.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# ----- robust Neon + django-tenants DB config -----
# env-driven
DATABASE_URL = config("DATABASE_URL", default=None)
DATABASE_URL_WRITER = config("DATABASE_URL_WRITER", default=None)
CONN_MAX_AGE = config("CONN_MAX_AGE", cast=int, default=120)
DISABLE_SERVER_SIDE_CURSORS = True

# base options we want in all cases
BASE_DB_OPTIONS = {
    "sslmode": "require",
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 10,
    "keepalives_count": 5,
}

# choose runtime DB URL (pooler) but allow overriding to writer when migrating
selected_db_url = DATABASE_URL or None
if os.environ.get("RUNNING_MIGRATIONS", "false").lower() == "true" and DATABASE_URL_WRITER:
    selected_db_url = DATABASE_URL_WRITER

if selected_db_url is None:
    # Fallback to explicit config (useful for dev without env vars)
    DATABASES = {
        "default": {
            "ENGINE": "django_tenants.postgresql_backend",
            "NAME": config("PGDATABASE", default="postgres"),
            "USER": config("PGUSER", default="postgres"),
            "PASSWORD": config("PGPASSWORD", default="postgres"),
            "HOST": config("PGHOST", default="localhost"),
            "PORT": config("PGPORT", default="5432"),
            "CONN_MAX_AGE": CONN_MAX_AGE,
            "OPTIONS": BASE_DB_OPTIONS,
        }
    }
else:
    # Parse URL then enforce the django-tenants engine and merge options
    parsed = dj_database_url.parse(selected_db_url, conn_max_age=CONN_MAX_AGE)
    parsed["ENGINE"] = "django_tenants.postgresql_backend"
    # merge/override OPTIONS
    options = parsed.get("OPTIONS", {})
    options.update(BASE_DB_OPTIONS)
    parsed["OPTIONS"] = options
    # apply some safety flags
    parsed["CONN_MAX_AGE"] = CONN_MAX_AGE
    parsed["DISABLE_SERVER_SIDE_CURSORS"] = DISABLE_SERVER_SIDE_CURSORS
    DATABASES = {"default": parsed}
# ---------------------------------------------------
DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

## REDIS CACHING
REDIS_CACHE_URL = config("REDIS_CACHE_URL", default=None)

if REDIS_CACHE_URL is not None:
     CACHES = {
         "default": {
             "BACKEND": "django_redis.cache.RedisCache",
             "LOCATION": REDIS_CACHE_URL,
             "OPTIONS": {
                 "CLIENT_CLASS": "django_redis.client.DefaultClient",
             }
         }
     }

DATABASES_psql = {
    'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': BASE_DIR / 'db.sqlite3',
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

DATABASES_mysql = {
         'default': {
             'ENGINE': 'django.db.backends.sqlite3',
             'NAME': BASE_DIR / 'db.sqlite3',
         }
     }

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators


APPOINTMENT_BUFFER_TIME = 0

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default
    'allauth.account.auth_backends.AuthenticationBackend', ] # Added for allauth

AUTH_USER_MODEL = 'Accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
# and renames the files with unique names for each version to support long-term caching

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),
            'secret': config('GOOGLE_SECRET'),
            'key': ''
        }
    }
}


LOGIN_REDIRECT_URL = '/accounts/profile'
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




TIME_INPUT_FORMATS = [
     "%I:%M %p",
]



Q_CLUSTER = {
    "name": "DjangoQ",
    "workers": 4,
    "timeout": 60,
    "retry": 90,   # retry > timeout
}

# CKEditor Configuration
SILENCED_SYSTEM_CHECKS = ["ckeditor.W001"]
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_JQUERY_URL = (
    "//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"
)

#CKEDITOR_CONFIGS = {
 #   "default": {
  #      "toolbar": "full",
   #     "height": 300,
    #    "width": "100%",
     #   "extraPlugins": ",".join(
      #      ["widget", "dialog", "dialogui", "codesnippet"]
       # ),
#    },
#}

CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
DEBUG_TOOLBAR_CONFIG = {
     "IS_RUNNING_TESTS": False,
}

CSRF_TRUSTED_ORIGINS = ['https://sleek.work.gd',  'http://127.0.0.1:8000']

#SECURE_SSL_REDIRECT = True
#SECURE_HSTS_SECONDS = 31536000
#SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#SECURE_HSTS_PRELOAD = True
#SECURE_BROWSER_XSS_FILTER = True
#SECURE_CONTENT_TYPE_NOSNIFF = True
#CSRF_COOKIE_SECURE = True
#SESSION_COOKIE_SECURE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'errors.log'),
        },
        'sms_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'sms.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'Appointment.utils': {
            'handlers': ['sms_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
# twillio Account Recovery CYLFDTYXGFV38LMFXFXJM4S6
SENDSMS_BACKEND = 'SmileSlot.mysmsbackend.SmsBackend'

# Email configuration
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # Options: "none", "optional", "mandatory"
ACCOUNT_LOGIN_METHODS = {'username', 'email'}

TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER')



EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_HOST_USER')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')




ADMIN_NAME=config("ADMIN_NAME", default="Mboa Technologies")
ADMIN_EMAIL=config("ADMIN_EMAIL", default=None)
MANAGERS=[]
ADMINS=[]
if all([ADMIN_NAME, ADMIN_EMAIL]):
    # 500 errors are emailed to these users
    ADMINS +=[
        (f'{ADMIN_NAME}', f'{ADMIN_EMAIL}')
    ]
    MANAGERS=ADMINS


EMAIL_SUBJECT_PREFIX = config('EMAIL_SUBJECT_PREFIX', '')
EMAIL_USE_LOCALTIME = config('EMAIL_USE_LOCALTIME', 'True').lower() == 'true'
SERVER_EMAIL = config('SERVER_EMAIL', EMAIL_HOST_USER)
USE_DJANGO_Q_FOR_EMAILS = config('USE_DJANGO_Q_FOR_EMAILS', 'True').lower() == 'true'
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)




BROWSER_RELOAD = True

API_KEY = config('API_KEY')
API_USERNAME = config('API_USERNAME')


###############################=================M-PESA DARAJA APIS CREDENTIALS=================###############################
MPESA_CONSUMER_KEY = config('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = config('MPESA_CONSUMER_SECRET')
MPESA_SHORTCODE_TYPE = config('MPESA_SHORTCODE_TYPE')

MPESA_SHORTCODE = config('MPESA_SHORTCODE')
MY_MPESA_TILL_NUMBER = config('MY_MPESA_TILL_NUMBER')
MPESA_PASSKEY = config('MPESA_PASSKEY')
MPESA_INITIATOR_USERNAME = config('MPESA_INITIATOR_USERNAME')
MPESA_INITIATOR_SECURITY_CREDENTIAL = config('MPESA_INITIATOR_SECURITY_CREDENTIAL')
LNM_PHONE_NUMBER = config('LNM_PHONE_NUMBER')
MPESA_EXPRESS_SHORTCODE = config('MPESA_EXPRESS_SHORTCODE')


AT_YOUR_USERNAME = config('AT_YOUR_USERNAME')
AT_YOUR_API_KEY = config('AT_YOUR_API_KEY')

STRIPE_PUBLIC_KEY = config('STRIPE_LIVE_PUBLIC_KEY')
STRIPE_SECRET_KEY = config('STRIPE_LIVE_SECRET_KEY')


USE_THOUSAND_SEPARATOR = False


# debug panel
# -----------
DEBUG_TOOLBAR_PATCH_SETTINGS = False
DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': '/static/vendor/jquery.js',
    'SHOW_COLLAPSED': True,
    'SHOW_TEMPLATE_CONTEXT': True,
}


# Allow user to enter month in durationfield
DURATIONFIELD_ALLOW_MONTHS = True


CURRENCY_JSON_PATH = os.path.join(BASE_DIR, 'static/saas/data/currencies.json')

# Configuration of djaodjin-saas
SAAS = {
    'BROKER': {
        'GET_INSTANCE': 'cowork',
    },
    'PROCESSOR_ID': 1,
    'MAIL_PROVIDER_DOMAINS': ['localhost.localdomain'],
    'PROCESSOR': {
        'BACKEND': 'saas.backends.stripe_processor.StripeBackend',
        'MODE': config('MODE', 0), # `LOCAL`
        'USE_STRIPE_V2': config('USE_STRIPE_V2', ''),
        'PRIV_KEY': config('STRIPE_PRIV_KEY', ''),
        'PUB_KEY': config('STRIPE_PUB_KEY', ''),
        'CLIENT_ID': config('STRIPE_CLIENT_ID', None),
        'WEBHOOK_SECRET': config('STRIPE_ENDPOINT_SECRET', ''),

         # Comment above and uncomment below to use FlutterWave instead.
 #        'BACKEND': 'saas.backends.razorpay_processor.RazorpayBackend',
 #        'PRIV_KEY': config('RAZORPAY_PRIV_KEY', None),
 #        'PUB_KEY': config('RAZORPAY_PUB_KEY', None),

         # Comment above and uncomment below to use RazorPay instead.
 #        'BACKEND': 'saas.backends.flutterwave_processor.FlutterwaveBackend',
 #        'PRIV_KEY': config('FLUTTERWAVE_PRIV_KEY', None),
 #        'PUB_KEY': config('FLUTTERWAVE_PUB_KEY', None),
    },
'EXPIRE_NOTICE_DAYS': [90, 60, 30, 15, 1],
}
