from django.contrib import admin

from ..models.Assembly import Assembly
from utils.mixins.AuditableMixin import AuditableMixin


@admin.register(Assembly)
class AssemblyAdmin(AuditableMixin, admin.ModelAdmin):
    actions = None
    fields = ["vehicle_family", "name", "code"]
    list_display = ("name", "code", "vehicle_family", "modified_on", "modified_by")
    list_select_related = ["vehicle_family", "modified_by"]
    list_filter = ["vehicle_family", "modified_on"]
    search_fields = ["name", "code"]
