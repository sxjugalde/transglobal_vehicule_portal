from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from orders.models.Order import Order


class PreviousOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "customer_pages/previous_orders.html"
    context_object_name = "previous_orders_list"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] = "previous_orders"
        context["user_company"] = None

        if self.request.user.company:
            context["user_company"] = self.request.user.company

        return context

    def get_queryset(self):
        """Returns the user's company's orders."""
        if self.request.user.company:
            return Order.objects.filter(company=self.request.user.company).order_by(
                "-created_on"
            )
        else:
            return Order.objects.none()
