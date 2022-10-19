"""
Django settings for vehicle_service_portal project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from django.contrib.messages import constants as messages
import environ

# Get the root of the project
root = environ.Path(__file__) - 3
SITE_ROOT = root()

# Read environment variables
env = environ.Env()
env.read_env(str(SITE_ROOT + "/.env"))  # reading .env file

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = []

# Application definition

# TODO: Improve - Add django-compressor. Implement minification and bundling.
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "django.contrib.admin",
    "django.forms",
    "smart_selects",
    "vehicles.apps.VehiclesConfig",
    "companies.apps.CompaniesConfig",
    "parts.apps.PartsConfig",
    "orders.apps.OrdersConfig",
    "utils.apps.UtilsConfig",
    "files.apps.FilesConfig",
    "customer_pages.apps.CustomerPagesConfig",
    "reports.apps.ReportsConfig",
    "users.apps.UsersConfig",
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

ROOT_URLCONF = "vehicle_service_portal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(root.path("templates/"))],
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

WSGI_APPLICATION = "vehicle_service_portal.wsgi.application"

ADMINS = [x.split(":") for x in env.list("DJANGO_ADMINS", default=[])]
MANAGERS = [x.split(":") for x in env.list("DJANGO_MANAGERS", default=[])]

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": env.str("DATABASE_HOST"),  # noqa
        "USER": env.str("DATABASE_USER"),  # noqa
        "PASSWORD": env.str("DATABASE_PASSWORD"),  # noqa
        "PORT": env.str("DATABASE_PORT"),  # noqa
        "NAME": env.str("DATABASE_NAME"),  # noqa
        "ATOMIC_REQUESTS": True,
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "EST5EDT"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# LOGGING
# https://docs.djangoproject.com/en/dev/ref/settings/#logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

public_root = root.path("public/")
MEDIA_ROOT = str(public_root("media"))
MEDIA_URL = env.str("MEDIA_URL", default="/media/")

STATIC_ROOT = str(public_root("static"))
STATIC_URL = env.str("STATIC_URL", default="/static/")
STATICFILES_DIRS = (str(root.path("static/")),)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Custom user model
AUTH_USER_MODEL = "users.CustomUser"

# Versioning
VERSION = "0.4.0"

# Form / Widget rendering
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# Emails
EMAIL_BACKEND = env.str(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = env.str("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_SUBJECT_PREFIX = f'{env.str("EMAIL_SUBJECT_PREFIX", default="[TG]")} '

# Auth
LOGIN_REDIRECT_URL = "auth-redirect"
LOGOUT_REDIRECT_URL = "login"

# Messages
MESSAGE_TAGS = {
    messages.DEBUG: "debug alert-secondary",
    messages.INFO: "info alert-info",
    messages.SUCCESS: "success alert-success",
    messages.WARNING: "warning alert-warning",
    messages.ERROR: "error alert-danger",
}
