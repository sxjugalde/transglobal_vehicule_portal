from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import HttpResponse

from ..logic.CartLogic import upsert_or_delete_cart_rows
from vehicles.models.Vehicle import Vehicle


class UpsertCartRowsView(LoginRequiredMixin, View):
    def post(self, request):
        """Changes or adds the cart's row with what's submitted via POST."""

        # Obtain POST data
        vehicle_id = request.POST.get("vehicleId", 0)
        bom_row_id = request.POST.get("bomRowId", 0)
        quantity = request.POST.get("quantity", 0)
        quantity = quantity if quantity else 0

        # Get Vehicle
        customer_company = request.user.company
        vehicle = get_object_or_404(
            Vehicle.objects.select_related("location__company"),
            id=vehicle_id,
        )

        if customer_company and customer_company == vehicle.location.company:
            upsert_or_delete_cart_rows(
                user=self.request.user,
                vehicle_id=vehicle_id,
                bom_row_id=bom_row_id,
                quantity=quantity,
            )

            return HttpResponse()
        else:
            raise PermissionDenied(
                "You don't have permission to view this vehicle. Please contact the system administrator."
            )
