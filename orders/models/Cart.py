from django.db import models

from utils.models.AuditableModel import AuditableModel


class Cart(AuditableModel):
    """A collection of cart row entries inputted by a customer user."""

    is_current = models.BooleanField(null=False, blank=False, default=True)

    class Meta:
        verbose_name = "cart"
        verbose_name_plural = "carts"
        indexes = [
            models.Index(
                fields=[
                    "is_current",
                    "created_by",
                ]
            ),
        ]

    def __str__(self):
        return f"{self.pk} - {self.created_by} - {self.created_on}"
