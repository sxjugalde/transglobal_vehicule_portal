from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils.translation import gettext, gettext_lazy as _

from companies.models.Company import Company
from companies.admin_sites.CustomerCompanyFilterList import CustomerCompanyFilterList
from utils.mixins.AuditableMixin import AuditableMixin
from .forms.CustomUserCreationForm import CustomUserCreationForm
from .forms.CustomUserChangeForm import CustomUserChangeForm
from .models import CustomUser
from .logic.AccountActivationTokenGenerator import account_activation_token
from .logic.EmailLogic import send_account_confirmation_email
from .logic.GroupLogic import auto_assign_groups
import logging

logger = logging.getLogger('console')


class CustomUserAdmin(AuditableMixin, UserAdmin):
    actions = None
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "company",
        "is_active",
        "is_staff",
        # "is_superuser",
        "last_login",
    )
    list_select_related = ["company"]
    list_filter = (CustomerCompanyFilterList, "is_staff", "is_active", "groups")
    superuser_fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email", "company")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    staff_fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email", "company")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    STAFF_GROUP_NAME = "Staff"
    CUSTOMER_GROUP_NAME = "Customer"

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        # Only superusers can see permissions and groups.
        if request.user.is_superuser:
            return self.superuser_fieldsets
        elif request.user.is_staff:
            return self.staff_fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super(CustomUserAdmin, self).get_form(request, obj, **kwargs)
        if obj is not None:
            form.base_fields["company"].queryset = Company.objects.filter(
                is_customer=True
            )
        return form

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            super(CustomUserAdmin, self).save_model(request, obj, form, change)

            # OnEdit: Review user's groups. Superusers manually manage groups.
            if change and obj.id is not None:
                if not request.user.is_superuser:
                    auto_assign_groups(
                        obj, self.STAFF_GROUP_NAME, self.CUSTOMER_GROUP_NAME
                    )

                # Send welcome/confirmation email to user.
                if not obj.confirmation_email_sent and obj.email:
                    send_account_confirmation_email(request, obj)


admin.site.register(CustomUser, CustomUserAdmin)

ordered_apps = [
    'companies',
    'files',
    'orders',
    'parts',
    'users',
    'vehicles',
    'auth',

]


def get_app_list(self, request):
    
    app_dict = self._build_app_dict(request)
    
    app_list = [app_dict.get(app_label) for app_label in ordered_apps]
    
    return app_list


admin.AdminSite.get_app_list = get_app_list

