from django.db import models

from utils.models.AuditableModel import AuditableModel
from companies.models.Location import Location
from .BOM import BOM
from files.models import File
from django.utils.translation import gettext_lazy as _


class Vehicle(AuditableModel):
    """An individual vehicle that belongs to a customer."""

    identification_number = models.CharField(
        _('VIN#'),
        blank=False, unique=True, max_length=20)
    location = models.ForeignKey(
        Location,
        null=False,
        blank=False,
        related_name="vehicles",
        related_query_name="vehicle",
        on_delete=models.PROTECT,
        help_text="Location where the customer has this vehicle.",
        verbose_name=_("Company & Location"),
    )
    bom = models.ForeignKey(
        BOM,
        null=False,
        blank=False,
        related_name="vehicles",
        related_query_name="vehicle",
        on_delete=models.PROTECT,
        verbose_name="Bill of materials",
        help_text="BOM that represents this vehicle's structure.",
    )
    nickname = models.CharField(blank=True, max_length=100)
    files = models.ManyToManyField(
        File,
        blank=True,
        help_text="General files related to the vehicle.",
        related_name="vehicles",
        related_query_name="vehicle",
    )

    class Meta:
        verbose_name = "vehicle"
        verbose_name_plural = "vehicles"

    def __str__(self):
        return self.identification_number
