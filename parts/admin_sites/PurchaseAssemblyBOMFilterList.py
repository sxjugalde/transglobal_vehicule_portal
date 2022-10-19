from django.contrib import admin

from vehicles.models.BOM import BOM


class PurchaseAssemblyBOMFilterList(admin.SimpleListFilter):
    title = "BOM"
    parameter_name = "bom"

    def lookups(self, request, model_admin):
        boms = list(BOM.objects.distinct().values_list("pk", "code"))
        return boms

    def queryset(self, request, queryset):
        return (
            queryset.filter(
                purchaseassemblypart__bom_row__bom__pk=self.value()
            ).distinct()
            if self.value()
            else queryset
        )
