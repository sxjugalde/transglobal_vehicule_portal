import logging

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import HttpResponse

from ..models.Order import Order
from ..models.Cart import Cart
from ..logic.CartLogic import submit_cart


class SubmitOrderView(LoginRequiredMixin, View):
    def post(self, request):
        """Submit's the user's cart as an order."""

        # Get user/cart
        customer_company = request.user.company
        cart = get_object_or_404(Cart, created_by=request.user, is_current=True)

        try:
            submit_cart(cart, request)
            messages.success(
                request,
                "Successfully submitted quote request. You'll receive an email notification once our team has reviewed it.",
            )
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error: {e}")
            messages.error(
                request,
                "An error ocurred while submitting the quote request. Please try again, or contact the system administrator.",
            )
            return redirect("shopping_cart")

        return redirect("home")
