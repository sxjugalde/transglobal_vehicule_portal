from django.db import models
from django.core.validators import RegexValidator

from .VehicleFamily import VehicleFamily
from utils.models.AuditableModel import AuditableModel
from utils.logic.compare_entity_field import compare_entity_field
from django.utils.translation import gettext_lazy as _


class Assembly(AuditableModel):
    """Topmost level in the BOM hierarchy. Groups subassemblies and parts."""

    name = models.CharField(_('Parent Assembly Code'), blank=False, max_length=50)
    code = models.CharField(
        _('Parent Assembly Code'),
        blank=False,
        max_length=4,
        validators=[
            RegexValidator(
                regex=r"^\d{4}$",
                message="Code has to be 4 digits long.",
                code="nomatch",
            ),
        ],
        help_text="4 digit assembly code. For example: 1010.",
    )
    vehicle_family = models.ForeignKey(
        VehicleFamily,
        null=False,
        blank=False,
        related_name="assemblies",
        related_query_name="assembly",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "assembly"
        verbose_name_plural = "assemblies"
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle_family", "code"], name="unique_vehiclefamily_assembly"
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "vehicle_family",
                ]
            ),
            models.Index(
                fields=[
                    "code",
                ]
            ),
            models.Index(
                fields=[
                    "vehicle_family",
                    "code",
                ]
            ),
        ]

    def __str__(self):
        return "[{}] {}".format(self.code, self.name)

    def validate_import_comparison(assembly, assembly_to_validate):
        """Compares two assemblies, returning differences in set of str, when the second entity has non-empty contents that differ with the first."""
        differing_fields = []

        differing_fields.extend(
            compare_entity_field(assembly, assembly_to_validate, "name")
        )

        return differing_fields


def get_assembly_str(code: str="", name: str="") -> str:
    """Returns __str__ representation without an instance."""
    return "[{}] {}".format(code, name)
