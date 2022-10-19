from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS += ["localhost", "0.0.0.0", "127.0.0.1"]  # noqa F405

# django-debug-toolbar
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["debug_toolbar"]  # noqa F405

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

# django-extensions
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["django_extensions"]  # noqa F405

CORS_REPLACE_HTTPS_REFERER = False
HOST_SCHEME = "http://"
SECURE_PROXY_SSL_HEADER = None
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = None
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_FRAME_DENY = False
