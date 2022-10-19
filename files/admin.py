from django.contrib import admin

from .models import File
from utils.mixins.AuditableMixin import AuditableMixin


@admin.register(File)
class FileAdmin(AuditableMixin, admin.ModelAdmin):
    fields = ["file"]
    list_display = (
        "name",
        "created_on",
        "modified_on",
        "modified_by",
    )
    list_select_related = ["modified_by"]
    list_filter = ["extension", "created_on", "modified_on"]
    search_fields = ["name"]
