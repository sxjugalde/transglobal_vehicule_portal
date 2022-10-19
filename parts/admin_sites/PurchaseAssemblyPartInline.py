from django.contrib import admin

from ..models.PurchaseAssemblyPart import PurchaseAssemblyPart


class PurchaseAssemblyPartInline(admin.TabularInline):
    model = PurchaseAssemblyPart
    min_num = 2
    extra = 0
    verbose_name = "Part"
    verbose_name_plural = "Parts"
    autocomplete_fields = ["part"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["part"]
        else:
            return []

    def has_delete_permission(self, request, obj=None):
        return False
