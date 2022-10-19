from django.contrib import admin

from .SuppliedPartsInline import SuppliedPartsInline
from ..models.Company import Company
from utils.mixins.AuditableMixin import AuditableMixin


@admin.register(Company)
class CompanyAdmin(AuditableMixin, admin.ModelAdmin):
    actions = None
    fields = ["name", "is_customer", "is_supplier", "logo"]
    list_display = (
        "name",
        "is_customer",
        "is_supplier",
        "modified_on",
        "modified_by",
    )
    list_select_related = ["modified_by"]
    list_filter = ["is_customer", "is_supplier", "modified_on"]
    search_fields = ["name"]

    def get_inline_instances(self, request, obj=None):
        _inlines = super().get_inline_instances(request, obj=None)
        if obj:
            old_object = self.model.objects.get(id=obj.id)
            if obj.is_supplier or (old_object.is_supplier and not obj.is_supplier):
                supplied_parts_inline = SuppliedPartsInline(self.model, self.admin_site)
                _inlines.append(supplied_parts_inline)
        return _inlines
