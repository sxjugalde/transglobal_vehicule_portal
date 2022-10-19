from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from vehicles.logic.VehicleLogic import search_company_vehicles


class SearchCompanyVehiclesView(LoginRequiredMixin, View):
    def get(self, request):
        """Obtains the search_text from the GET params and returns the vehicles from the user's company that match by VIN or nickname."""
        # Obtain search_text
        search_text = request.GET.get("q", "")

        # Fetch company vehicles and return as JSON.
        vehicles_values = []
        if request.user.company:
            vehicles = search_company_vehicles(request.user.company.id, search_text)
            vehicles_values = list(
                vehicles.values("id", "identification_number", "nickname")
            )

        return JsonResponse(vehicles_values, safe=False)
