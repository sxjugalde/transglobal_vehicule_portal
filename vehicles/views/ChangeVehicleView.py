from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from vehicles.models.Vehicle import Vehicle


class ChangeVehicleView(LoginRequiredMixin, View):
    def post(self, request, vehicle_id):
        """Changes the vehicle's information with what's submitted via POST."""

        # Get Vehicle
        customer_company = request.user.company
        vehicle = get_object_or_404(
            Vehicle.objects.select_related("location__company"),
            id=vehicle_id,
        )

        if customer_company and customer_company == vehicle.location.company:
            # Obtain POST data
            nickname = request.POST.get("nickname", vehicle.nickname)

            # Change entity
            vehicle.nickname = nickname
            vehicle.modified_by = self.request.user
            vehicle.save()

            messages.success(
                request,
                f"Vehicle {vehicle.identification_number} changed successfully.",
            )

            return redirect("vehicle_details", vehicle.identification_number)
        else:
            raise PermissionDenied(
                "You don't have permission to view this vehicle. Please contact the system administrator."
            )
