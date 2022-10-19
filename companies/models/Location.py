from django.db import models

from .Company import Company
from utils.models.AuditableModel import AuditableModel
from django.utils.translation import gettext_lazy as _


class Location(AuditableModel):
    """A location belonging to a customer company, which contains vehicles."""

    name = models.CharField(_('Location'), blank=False, max_length=100)
    company = models.ForeignKey(
        Company,
        null=False,
        blank=False,
        related_name="locations",
        related_query_name="location",
        on_delete=models.PROTECT,
        help_text="Customer company that owns this location.",
    )
    identification = models.CharField(blank=True, editable=False, max_length=150)

    class Meta:
        verbose_name = "location"
        verbose_name_plural = "locations"
        indexes = [
            models.Index(
                fields=[
                    "company",
                ]
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"], name="unique_company_location"
            ),
        ]

    def save(self, *args, **kwargs):
        self.identification = f"[{self.company.name}] - {self.name}"
        super(Location, self).save(*args, **kwargs)

    def __str__(self):
        return self.identification
