import importlib.util

modules = [
    "rest_framework",
    "rest_framework_simplejwt",
    "admin_honeypot",
    "disaster_app",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "cloudinary",
    "cloudinary_storage",
    "axes",
    "whitenoise",
]

for module in modules:
    print(module, "OK" if importlib.util.find_spec(module) else "MISSING")
