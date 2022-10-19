from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import get_object_or_404, render, redirect

from utils.mixins.AuditableMixin import AuditableMixin
from companies.admin_sites.CustomerCompanyFilterList import CustomerCompanyFilterList
from ..models.Order import Order
from ..logic.CartLogic import get_cart_details
from ..logic.EmailLogic import send_quote_request_reviewed_email


@admin.register(Order)
class OrderAdmin(AuditableMixin, admin.ModelAdmin):
    actions = None
    list_display_links = None
    fields = ["order_status"]
    list_display = (
        "id",
        "order_status",
        "user_username",
        "user_email",
        "company",
        "created_on",
        "modified_on",
        "modified_by",
        "actions_html",
    )
    list_select_related = ["company", "modified_by"]
    list_filter = [
        "order_status",
        CustomerCompanyFilterList,
        "created_on",
        "modified_on",
    ]
    search_fields = [
        "id__exact",
        "user_username",
        "user_email",
        "company_name",
    ]

    def actions_html(self, obj):
        actions_html = format_html(
            '<a class="button" href="{order_details_url}" title="View details" aria-label="View details"><i class="fa fa-eye"></i></a>',
            order_details_url=reverse(
                "admin:order_details",
                args=(obj.id,),
            ),
        )

        return actions_html

    actions_html.allow_tags = True
    actions_html.short_description = "Actions"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:order_id>/set_reviewed/",
                self.admin_site.admin_view(self.set_reviewed),
                name="orders_set_reviewed",
            ),
            path(
                "<int:order_id>/details/",
                self.admin_site.admin_view(self.get_details),
                name="order_details",
            ),
        ]
        return custom_urls + urls

    def has_add_permission(self, request, obj=None):
        return False

    def set_reviewed(self, request, order_id: int):
        """Sets an order as reviewed."""
        order = get_object_or_404(Order, pk=order_id)

        try:
            order.order_status = Order.ORDER_STATUS_REVIEWED
            order.save()

            messages.success(
                request, f"Order #{order_id} successfully marked as reviewed."
            )
        except Exception as e:
            error_message = str(e)
            messages.error(
                request,
                f"An error ocurred while marking order #{order_id} as reviewed: {error_message}",
            )

        send_quote_request_reviewed_email(
            request, order.user_username, order.user_email, order.id
        )

        return redirect("admin:order_details", order_id=order_id, permanent=True)

    def get_details(self, request, order_id: int):
        """Returns the order details screen."""
        order = get_object_or_404(Order, pk=order_id)

        # Setup context and render template
        context = self.admin_site.each_context(request)
        context["opts"] = self.model._meta
        context["title"] = f"Order #{order_id} - Details"
        context["order"] = order
        context["cart_details"] = get_cart_details(order.cart)
        context["cart_details_header_classes"] = ["module", "admin-cart-detail-header"]
        context["cart_details_row_classes"] = ["admin-cart-detail-row"]

        return render(request, "admin/orders_order_details.html", context)
