from django.db import models
from django.core.validators import FileExtensionValidator, ValidationError

from .VehicleFamily import VehicleFamily
from utils.models.AuditableModel import AuditableModel
from utils.models.ThumbnailModel import ThumbnailModel
from files.models import File
from django.utils.translation import gettext_lazy as _


class BOM(AuditableModel, ThumbnailModel):
    """Bill of materials. Defines the structure of a vehicle model, or a particular vehicle."""

    # BOM import file paths
    BOM_IMPORT_FOLDER = "uploads/boms/"
#renaming from BOM CODE to Model Code
    name = models.CharField(_('BOM Name'), blank=False, max_length=50)
    code = models.CharField(_('Model Code'), blank=False, max_length=20)
    description = models.TextField(blank=True)
    revision = models.CharField(
        _('BOM Rev Level'),
        blank=True,
        max_length=1,
        help_text="Revision code. For example: A.",
    )
    revision_notes = models.TextField(blank=True)
    import_file = models.FileField(
        blank=True,
        upload_to=BOM_IMPORT_FOLDER,
        validators=[
            FileExtensionValidator(allowed_extensions=["csv", "xlsx", "xlsm", "xls"])
        ],
    )
    vehicle_family = models.ForeignKey(
        VehicleFamily,
        null=True,  # Must be nullable and blank due to duplication (save_as), but this validation is handled in form.
        blank=True,
        related_name="boms",
        related_query_name="bom",
        on_delete=models.PROTECT,
    )
    files = models.ManyToManyField(
        File,
        blank=True,
        help_text="General files related to the BOM.",
        related_name="boms",
        related_query_name="bom",
    )

    class Meta:
        verbose_name = "Bill of materials"
        verbose_name_plural = "Bills of materials"
        constraints = [
            models.UniqueConstraint(
                fields=["code", "revision"], name="unique_bom_code_revision"
            ),
        ]

    def __str__(self):
        return f"[{self.code + self.revision}] {self.name}"

    def save(self, *args, **kwargs):
        # Validations are done here because the fields themselves must be nullable when submitting the form, so clean or field validation doesn't work. Reason: readonly fields in save_as.
        if not self.vehicle_family:
            raise ValidationError("The vehicle family is required.")

        if not self.import_file:
            raise ValidationError("The import file is required.")
        super(BOM, self).save(*args, **kwargs)
