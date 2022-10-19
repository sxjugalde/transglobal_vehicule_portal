from django.contrib import admin
from django.db import models
from django.forms import Textarea

from companies.models.Company import Company
from utils.mixins.SetAuditableUserFormsetMixin import SetAuditableUserFormsetMixin
from ..models.PartSupplier import PartSupplier


class PartSupplierInline(SetAuditableUserFormsetMixin, admin.TabularInline):
    model = PartSupplier
    min_num = 0
    extra = 0
    verbose_name = "Supplier"
    verbose_name_plural = "Suppliers"
    fields = [
        "company",
        "supplier_part_number",
        "purchase_comments",
    ]
    autocomplete_fields = ["company"]
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
