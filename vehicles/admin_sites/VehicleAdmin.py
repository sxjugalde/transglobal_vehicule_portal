from django.contrib import admin

from ..models.Vehicle import Vehicle
from utils.mixins.AuditableMixin import AuditableMixin


@admin.register(Vehicle)
class VehicleAdmin(AuditableMixin, admin.ModelAdmin):
    actions = None
    fields = ["identification_number", "location", "bom", "nickname", "files"]
    filter_horizontal = ("files",)
    list_display = (
        "identification_number",
        "nickname",
        "location",
        "bom",
        "modified_on",
        "modified_by",
    )
    list_select_related = ["location", "bom", "modified_by"]
    list_filter = ["location", "bom", "modified_on"]
    search_fields = ["identification_number"]
