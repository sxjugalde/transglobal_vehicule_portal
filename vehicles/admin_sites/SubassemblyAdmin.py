from django.contrib import admin

from ..models.Subassembly import Subassembly
from utils.mixins.AuditableMixin import AuditableMixin


@admin.register(Subassembly)
class SubassemblyAdmin(AuditableMixin, admin.ModelAdmin):
    actions = None
    fields = ["vehicle_family", "assembly", "name", "code"]
    list_display = (
        "name",
        "full_code",
        "vehicle_family",
        "assembly",
        "modified_on",
        "modified_by",
    )
    list_select_related = ["vehicle_family", "assembly", "modified_by"]
    list_filter = ["vehicle_family", "modified_on"]
    search_fields = ["name", "full_code"]
