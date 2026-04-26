import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

env_path = BASE_DIR / ".env"
print("Loading .env from:", env_path)

load_dotenv(dotenv_path=env_path, override=True)

print("DB_NAME from env:", os.getenv("DB_NAME"))

BASE_DIR = Path(__file__).resolve().parent.parent
# Ensure backend/.env values win over stale exported shell vars.
load_dotenv(BASE_DIR / ".env", override=True)

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
# Allow all hosts for development (ngrok testing)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.device_manager",
    "apps.data_ingestion",
    "apps.mqtt_service",
    "apps.ai_orchestration",
    "apps.quality_center",
    "apps.storage_sync",
    "apps.governance",
    "apps.api_gateway",
    "apps.monitoring",
    "apps.authentication",
    "rest_framework_simplejwt",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database: keep NAME / HOST / USER / PASSWORD in sync with where your data lives.
# NOTE: The same PostgreSQL host can contain multiple databases.
# Tables such as `api_keys` / `users` / `devices` may exist only in one DB
# (for example `postgres`), so Django must use that exact DB NAME.
#
# If PostgreSQL has table `api_keys` but Django reports
#   relation "api_keys" does not exist
# then Django's default connection is a *different* database or server than the
# one you verified in psql/pgAdmin. Fix by setting DB_* in backend/.env to match
# the SAME AWS RDS database that contains your application tables
# (`api_keys`, `users`, `devices`, etc.), then restart the app.
#
# Verify in psql (same user/host as Django):
#   \conninfo          -- shows current DB, user, host, port
#   \c dbname          -- connect/switch database (e.g. \c postgres)
#   \dt api_keys       -- list table if it exists in current DB/search_path
#   SELECT current_database(), inet_server_addr();
#
# Django uses ENGINE django.db.backends.postgresql with the PostgreSQL driver
# you install. This project uses `psycopg` v3; if you use `psycopg2`, keep the
# same ENGINE and ensure the package is installed in the active virtualenv.
# Debug snippet (run with `python manage.py shell`) to inspect live connection:
#   from django.db import connection
#   print("DB:", {"NAME": connection.settings_dict.get("NAME"),
#                 "HOST": connection.settings_dict.get("HOST"),
#                 "USER": connection.settings_dict.get("USER")})
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "mxsense_admin",
        "PASSWORD": os.getenv("DB_PASSWORD", "mxsense123"),
        "HOST": "mxsense-db-updated.cfwsawyco4p4.ap-south-1.rds.amazonaws.com",
        "PORT": "5432",
    }
}

_db = DATABASES["default"]
print(
    "DJANGO DATABASE (default) — NAME:",
    _db["NAME"],
    "| HOST:",
    _db["HOST"],
    "| USER:",
    _db["USER"],
)
print("FINAL DATABASE:", DATABASES["default"]["NAME"])

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# User-uploaded / captured images (served under /media/ in DEBUG; use nginx/CDN in prod).
MEDIA_URL = os.getenv("DJANGO_MEDIA_URL", "/media/")
_media_root_name = os.getenv("DJANGO_MEDIA_ROOT", "media")
MEDIA_ROOT = BASE_DIR / _media_root_name

# Optional: treat bare object keys in DB as S3 keys and presign (requires boto3 + bucket).
AWS_S3_REGION_NAME = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
AWS_S3_IMAGE_BUCKET = os.getenv("AWS_S3_IMAGE_BUCKET", "")
USE_S3_IMAGE_KEY_PRESIGN = (
    os.getenv("USE_S3_IMAGE_KEY_PRESIGN", "false").lower() == "true"
)
AWS_PRESIGNED_URL_EXPIRY_SECONDS = int(
    os.getenv("AWS_PRESIGNED_URL_EXPIRY_SECONDS", "3600")
)

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("JWT_ACCESS_MINUTES", "60"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("JWT_REFRESH_DAYS", "7"))
    ),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "true").lower() == "true"
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000").split(",")
    if origin.strip()
]
print("DB_NAME:", os.getenv("DB_NAME"))