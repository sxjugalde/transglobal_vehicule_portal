from django.contrib import admin

from ..models.Location import Location
from ..models.Company import Company
from .CustomerCompanyFilterList import CustomerCompanyFilterList
from utils.mixins.AuditableMixin import AuditableMixin


@admin.register(Location)
class LocationAdmin(AuditableMixin, admin.ModelAdmin):
    actions = None
    fields = ["company", "name"]
    list_display = ("name", "company", "modified_on", "modified_by")
    list_select_related = ["company", "modified_by"]
    list_filter = [CustomerCompanyFilterList, "modified_on"]
    search_fields = ["name"]

    def get_form(self, request, obj=None, **kwargs):
        form = super(LocationAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["company"].queryset = Company.objects.filter(is_customer=True)
        return form
