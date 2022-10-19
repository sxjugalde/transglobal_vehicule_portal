from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from orders.models.Order import Order
from orders.logic.CartLogic import get_cart_details


class OrderDetailsView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        """Returns the order details view."""
        context = {}
        context["page_name"] = "order_details"

        customer_company = request.user.company
        order = get_object_or_404(
            Order.objects.select_related("cart"),
            id=order_id,
        )
        context["order"] = order
        context["order_cart_details"] = None

        if customer_company and customer_company == order.company:
            context["user_company"] = customer_company

            if order.cart:
                context["order_cart_details"] = get_cart_details(order.cart)
                context["order_cart_details_header_classes"] = []
                context["order_cart_details_row_classes"] = []
        else:
            raise PermissionDenied(
                "You don't have permission to view this order. Please contact the system administrator."
            )

        return render(request, "customer_pages/order_details.html", context)
