from django.contrib import admin
from django.urls import path
from django.core import serializers
from django.http import JsonResponse

from .PurchaseAssemblyPartInline import PurchaseAssemblyPartInline
from .PurchaseAssemblyBOMFilterList import PurchaseAssemblyBOMFilterList
from ..models.PurchaseAssembly import PurchaseAssembly
from ..models.PurchaseAssemblyPart import get_all_purchase_assembly_parts
from utils.mixins.AuditableMixin import AuditableMixin
from utils.logic.check_staff_permission import check_staff_permission


@admin.register(PurchaseAssembly)
class PurchaseAssemblyAdmin(AuditableMixin, admin.ModelAdmin):
    actions = None
    save_as = True
    fields = ["code"]
    list_display = (
        "__str__",
        "parts_contained",
        "get_boms",
        "modified_on",
        "modified_by",
    )
    list_select_related = ["modified_by"]
    inlines = (PurchaseAssemblyPartInline,)
    list_filter = [PurchaseAssemblyBOMFilterList, "modified_on"]
    search_fields = ["full_code", "parts_contained"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["code"]
        else:
            return []

    def get_queryset(self, request):
        return (
            super(PurchaseAssemblyAdmin, self)
            .get_queryset(request)
            .prefetch_related("purchaseassemblypart_set__bom_rows__bom")
        )

    def get_boms(self, obj):
        """Returns the BOMs where the PA has been used in for usage in list_display."""
        boms = set()
        pa_part_aux = obj.purchaseassemblypart_set.all()[0]

        for bom_row in pa_part_aux.bom_rows.all():
            if bom_row.bom.code not in boms:
                boms.add(bom_row.bom.code)

        boms_str = "-".join(boms) if boms else ""

        return boms_str

    get_boms.short_description = "Used in BOMs"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:purchase_assembly_id>/purchaseassemblypart/getall",
                self.admin_site.admin_view(self.get_purchase_assembly_parts),
                name="parts_purchaseassembly_parts",
            ),
        ]
        return custom_urls + urls

    def get_purchase_assembly_parts(self, request, purchase_assembly_id: int):
        """Returns the parts belonging to a PA."""
        check_staff_permission(request.user, "parts.view_purchaseassembly")

        # Fetch PA's parts and return as JSON.
        pa_parts = get_all_purchase_assembly_parts(purchase_assembly_id)
        pa_parts_values = list(
            pa_parts.values("id", "quantity", "part__full_code", "part__name")
        )

        return JsonResponse(pa_parts_values, safe=False)
