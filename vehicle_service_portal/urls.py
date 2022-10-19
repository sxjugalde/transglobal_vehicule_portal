"""vehicle_service_portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from users.forms.CustomLoginForm import CustomLoginForm

# Admin configs
admin.site.site_header = "Transglobal"
admin.site.site_title = "Transglobal Admin Portal"
admin.site.index_title = "Administration"
admin.site.login_template = "registration/login.html"
admin.site.login_form = CustomLoginForm

# URL patterns
urlpatterns = [
    # Admin & admin reset password.
    path("admin/", admin.site.urls),
    path("accounts/", include("users.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("customer_pages.urls")),
    path("vehicles/", include("vehicles.urls")),
    path("orders/", include("orders.urls")),
    path("reports/", include("reports.urls")),
    # Third party libraries.
    path("chaining/", include("smart_selects.urls")),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)  # Static media.

if settings.DEBUG:
    import debug_toolbar

    # Debug toolbar.
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
