from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from vehicles.logic.VehicleLogic import get_all_company_vehicles_by_location


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        """Returns the home page, which includes information on the customer's locations and vehicles."""
        context = {}
        context["page_name"] = "home"
        context["user_company"] = None
        context["vehicles_by_location"] = None
        if request.user.company:
            context["user_company"] = request.user.company
            context["vehicles_by_location"] = get_all_company_vehicles_by_location(
                request.user.company.id
            )

        return render(request, "customer_pages/home.html", context)
