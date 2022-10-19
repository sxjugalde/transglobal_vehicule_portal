from django.db import models

from .Cart import Cart
from companies.models.Company import Company
from utils.models.AuditableModel import AuditableModel


class Order(AuditableModel):
    """A quote order created by the user."""

    ORDER_STATUS_CREATED = "CREATED"
    ORDER_STATUS_REVIEWED = "REVIEWED"
    ORDER_STATUS_CHOICES = [
        (ORDER_STATUS_CREATED, "Created"),
        (ORDER_STATUS_REVIEWED, "Reviewed"),
    ]

    cart = models.OneToOneField(
        Cart,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
    )
    company = models.ForeignKey(
        Company,
        null=True,
        blank=False,
        related_name="orders",
        related_query_name="order",
        on_delete=models.SET_NULL,
        help_text="Customer company related to this order.",
    )
    order_status = models.CharField(
        max_length=15,
        choices=ORDER_STATUS_CHOICES,
        default=ORDER_STATUS_CREATED,
    )
    # Historic log fields.
    user_username = models.CharField(blank=True, max_length=150)
    user_email = models.EmailField(blank=True, max_length=254)
    company_name = models.CharField(blank=True, max_length=120)

    class Meta:
        verbose_name = "order"
        verbose_name_plural = "orders"
        indexes = [
            models.Index(
                fields=[
                    "user_username",
                ]
            ),
            models.Index(
                fields=[
                    "user_email",
                ]
            ),
            models.Index(
                fields=[
                    "company_name",
                ]
            ),
        ]

    def __str__(self):
        return f"{self.pk} - {self.user_username} - {self.order_status} - {self.created_by} - {self.created_on}"

    def save(self, *args, **kwargs):
        if self.created_by:
            self.user_username = self.created_by.username
            self.user_email = self.created_by.email

        if self.company:
            self.company_name = self.company.name

        super(Order, self).save(*args, **kwargs)
