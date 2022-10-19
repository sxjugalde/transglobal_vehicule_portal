from django.contrib import admin
from django.db import models
from django.forms import Textarea

from ..models.Company import Company
from utils.mixins.SetAuditableUserFormsetMixin import SetAuditableUserFormsetMixin
from parts.models.PartSupplier import PartSupplier


class SuppliedPartsInline(SetAuditableUserFormsetMixin, admin.TabularInline):
    model = PartSupplier
    min_num = 0
    extra = 0
    verbose_name = "Part"
    verbose_name_plural = "Supplied Parts"
    fields = [
        "part",
        "supplier_part_number",
        "purchase_comments",
    ]
    autocomplete_fields = ["part"]
    formfield_overrides = {
        models.TextField: {
            "widget": Textarea(
                attrs={
                    "rows": 2,
                    "cols": 40,
                }
            )
        },
    }
