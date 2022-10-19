from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from orders.models.Cart import Cart
from orders.logic.CartLogic import get_cart_details


class ShoppingCartView(LoginRequiredMixin, View):
    def get(self, request):
        """Returns the shopping cart details."""
        context = {}
        context["page_name"] = "shopping_cart"
        context["user_company"] = None
        context["user_cart"] = None
        context["cart_details"] = None

        if request.user.company:
            context["user_company"] = request.user.company
            active_cart = Cart.objects.filter(
                created_by=request.user, is_current=True
            ).first()
            context["user_cart"] = active_cart

            if active_cart:
                context["cart_details"] = get_cart_details(active_cart)
                context["cart_details_header_classes"] = []
                context["cart_details_row_classes"] = []

        return render(request, "customer_pages/shopping_cart.html", context)
