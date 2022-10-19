from django.contrib import admin
from django.db import models
from django import forms

from ..models.VehicleFamily import VehicleFamily
from utils.mixins.AuditableMixin import AuditableMixin


@admin.register(VehicleFamily)
class VehicleFamilyAdmin(AuditableMixin, admin.ModelAdmin):
    actions = None
    fields = [
        "name",
        "code",
        "description",
        "thumbnail",
    ]
    list_display = (
        "name",
        "code",
        "modified_on",
        "modified_by",
        "image_tag",
    )
    list_select_related = ["modified_by"]
    list_filter = ["modified_on"]
    search_fields = ["name", "code"]
    formfield_overrides = {
        models.TextField: {
            "widget": forms.Textarea(
                attrs={
                    "rows": 2,
                    "cols": 80,
                }
            )
        },
    }
