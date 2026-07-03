"""
Django settings for config project.
"""

from pathlib import Path
import importlib.util
import os
from dotenv import load_dotenv
import django.utils.translation
import django.dispatch
import django.conf.urls
from django.urls import re_path

# Monkey patch for legacy packages (like admin-honeypot) that use removed 
# translation functions in Django 4.0+.
if not hasattr(django.utils.translation, 'ugettext_lazy'):
    django.utils.translation.ugettext_lazy = django.utils.translation.gettext_lazy
    django.utils.translation.ugettext = django.utils.translation.gettext

# Monkey patch for Signal to ignore providing_args which was removed in Django 4.0.
# This is required for legacy packages like admin-honeypot.
_old_init = django.dispatch.Signal.__init__
def _new_init(self, *args, **kwargs):
    kwargs.pop('providing_args', None)
    _old_init(self, *args, **kwargs)
django.dispatch.Signal.__init__ = _new_init

# Monkey patch for django.conf.urls.url which was removed in Django 4.0.
if not hasattr(django.conf.urls, 'url'):
    django.conf.urls.url = re_path

try:
    import dj_database_url  # pyright: ignore[reportMissingImports]
except ModuleNotFoundError:
    dj_database_url = None

AXES_AVAILABLE = importlib.util.find_spec("axes") is not None
CORS_HEADERS_AVAILABLE = importlib.util.find_spec("corsheaders") is not None
ADMIN_HONEYPOT_AVAILABLE = importlib.util.find_spec("admin_honeypot") is not None
WHITENOISE_AVAILABLE = importlib.util.find_spec("whitenoise") is not None
CLOUDINARY_AVAILABLE = importlib.util.find_spec("cloudinary") is not None and importlib.util.find_spec("cloudinary_storage") is not None

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================================
# CORE SETTINGS
# =========================================================

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-default-key-change-this'
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1'
).split(',')

# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [
    # DRF (Phase 2 Core)
    'rest_framework',
    'rest_framework_simplejwt',

    # Apps
    'disaster_app',

    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

if ADMIN_HONEYPOT_AVAILABLE and 'admin_honeypot' not in INSTALLED_APPS:
    INSTALLED_APPS.append('admin_honeypot')

if CORS_HEADERS_AVAILABLE and 'corsheaders' not in INSTALLED_APPS:
    INSTALLED_APPS.append('corsheaders')

if CLOUDINARY_AVAILABLE:
    INSTALLED_APPS.extend(['cloudinary', 'cloudinary_storage'])

if AXES_AVAILABLE and 'axes' not in INSTALLED_APPS:
    INSTALLED_APPS.append('axes')

# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if WHITENOISE_AVAILABLE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

if CORS_HEADERS_AVAILABLE and 'corsheaders.middleware.CorsMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(2, 'corsheaders.middleware.CorsMiddleware')

if AXES_AVAILABLE and 'axes.middleware.AxesMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.append('axes.middleware.AxesMiddleware')

ROOT_URLCONF = 'config.urls'

# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# =========================================================
# SECURITY: ACTIVE DEFENSE (django-axes)
# =========================================================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

if AXES_AVAILABLE:
    AUTHENTICATION_BACKENDS.insert(
        0,
        'axes.backends.AxesStandaloneBackend'
    )

AXES_FAILURE_LIMIT = 5  # Lockout after 5 failed attempts
AXES_COOLOFF_TIME = 0.5 # 30 minutes lockout
AXES_LOCKOUT_TEMPLATE = None # Can be a custom HTML template
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = ["ip_address", "username"]

# =========================================================
# LOGIN SETTINGS
# =========================================================

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'admin_dashboard'
LOGOUT_REDIRECT_URL = 'login'

# =========================================================
# SECURITY: RATE LIMITING (DRF Throttling)
# =========================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/minute',   # Strict for non-auth public
        'user': '100/minute'   # Standard for logged-in staff
    }
}

# =========================================================
# DATABASE
# =========================================================

if dj_database_url is not None:
    DATABASES = {
        'default': dj_database_url.config(
            default='sqlite:///db.sqlite3',
            conn_max_age=600
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'disaster_app' / 'static']

if WHITENOISE_AVAILABLE:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =========================================================
# MEDIA (Cloudinary or Local)
# =========================================================

if os.environ.get('CLOUDINARY_URL') and CLOUDINARY_AVAILABLE:
    import cloudinary  # pyright: ignore[reportMissingImports]
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    )

    STORAGES = {
        'default': {
            'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
        }
    }

    MEDIA_URL = '/media/'
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# =========================================================
# DEFAULT AUTO FIELD
# =========================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================================================
# CORS
# =========================================================

CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000'
).split(',')

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost,http://127.0.0.1'
).split(',')

# =========================================================
# LOGGING (FIXED - NO ERRORS)
# =========================================================

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },

        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'django.log'),
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'disaster_app': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'axes': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}

# =========================================================
# CACHE (SAFE FALLBACK)
# =========================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'disaster-cache',
    }
}

SESSION_CACHE_ALIAS = 'default'

# =========================================================
# DRF + JWT (PHASE 2 CORE REQUIREMENT)
# =========================================================

# Note: REST_FRAMEWORK settings merged into the block above (lines 128-142)
