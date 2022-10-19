from django.db import models

from utils.models.AuditableModel import AuditableModel
from utils.models.ThumbnailModel import ThumbnailModel
from django.utils.translation import gettext_lazy as _


class VehicleFamily(AuditableModel, ThumbnailModel):
    """A group of vehicles which have common specifications."""

    name = models.CharField(_('Family Name'), blank=False, max_length=50)
    description = models.TextField(blank=True)
    code = models.CharField(_('Model Code'), blank=True, max_length=20)

    class Meta:
        verbose_name = "vehicle family"
        verbose_name_plural = "vehicle families"

    def __str__(self):
        return self.name
