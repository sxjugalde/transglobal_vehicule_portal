from django.contrib import admin

from ..models.Company import Company


class CustomerCompanyFilterList(admin.SimpleListFilter):
    title = "customer company"
    parameter_name = "company"

    def lookups(self, request, model_admin):
        customer_companies = Company.objects.filter(is_customer=True)
        return ((company.pk, company.name) for company in customer_companies)

    def queryset(self, request, queryset):
        return queryset.filter(company_id=self.value()) if self.value() else queryset
