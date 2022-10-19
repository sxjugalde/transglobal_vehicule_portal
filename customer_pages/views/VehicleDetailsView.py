from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from vehicles.models.Vehicle import Vehicle
from vehicles.logic.BOMLogic import get_bom_structure


class VehicleDetailsView(LoginRequiredMixin, View):
    def get(self, request, vin):
        """Returns the vehicle's details, including structure and related files."""
        context = {}
        context["page_name"] = "vehicle_details"

        customer_company = request.user.company
        vehicle = get_object_or_404(
            Vehicle.objects.select_related("location")
            .select_related("bom")
            .select_related("location__company")
            .prefetch_related("files")
            .prefetch_related("bom__files"),
            identification_number=vin,
        )

        if customer_company and customer_company == vehicle.location.company:
            context["user_company"] = customer_company
            context["vehicle"] = vehicle
            context["bom"] = vehicle.bom

            # BOM Structure
            context["bom_structure"] = get_bom_structure(
                bom=vehicle.bom, user=request.user, vehicle_identification_number=vin
            )
            context["row_actions"] = ["change-qty"]

            # BOM Files
            files = {}
            for file in vehicle.bom.files.all():
                if file.name not in files:
                    files[file.name] = file.file.url

            for file in vehicle.files.all():
                if file.name not in files:
                    files[file.name] = file.file.url
            context["files"] = files

            return render(request, "customer_pages/vehicle_details.html", context)
        else:
            raise PermissionDenied(
                "You don't have permission to view this vehicle. Please contact the system administrator."
            )
