import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = (
    "django-insecure-a*9^gray^%e19^lw0^7+e)a!%a$!(tohv$1c8(32k@831_(3id"
)

DEBUG = True

ALLOWED_HOSTS = []

# from dotenv import load_dotenv

# load_dotenv()

# SECRET_KEY = os.getenv("SECRET_KEY", "key_for_autotests")

# DEBUG = os.getenv("DEBUG")

# ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') # WARNING: должны быть одинарные кавычки

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    'django_filters',
    "api",
    "recipes",
    "users",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodgram.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "foodgram.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.getenv("POSTGRES_DB", "kittygram"),
#         "USER": os.getenv("POSTGRES_USER", "kittygram_user"),
#         "PASSWORD": os.getenv("POSTGRES_PASSWORD", "kittygram_password"),
#         "HOST": os.getenv("DB_HOST", "db"),
#         "PORT": os.getenv("DB_PORT", 5432),
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "users.User"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = "/static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "api.pagination.CustomPagination",
    "PAGE_SIZE": 6,
}

DJOSER = {
    "LOGIN_FIELD": "email",
    "SERIALIZERS": {
        "user": "api.serializers.CustomUserSerializer",
        "current_user": "api.serializers.CustomUserSerializer",
        "user_create": "api.serializers.CustomUserCreateSerializer",
    },
    "PERMISSIONS": {
        "user_list": ["rest_framework.permissions.AllowAny"],
        "user": ["djoser.permissions.CurrentUserOrAdminOrReadOnly"],
    },
}
