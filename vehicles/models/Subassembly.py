from django.db import models
from django.core.validators import RegexValidator

from smart_selects.db_fields import ChainedForeignKey

from .VehicleFamily import VehicleFamily
from .Assembly import Assembly
from utils.models.AuditableModel import AuditableModel
from utils.logic.compare_entity_field import compare_entity_field
from django.utils.translation import gettext_lazy as _


class Subassembly(AuditableModel):
    """Mid level in the BOM hierarchy. Groups parts, and is contained in assemblies."""

    name = models.CharField(_('Sub Assembly Code'), blank=False, max_length=50)
    code = models.CharField(
        _('Sub Assembly Code'),
        blank=False,
        max_length=3,
        validators=[
            RegexValidator(
                regex="^[S]{1}\d{2}$",
                message="Code has to begin with S and be followed by 2 digits.",
                code="nomatch",
            ),
        ],
        help_text="Format: SXX, where XX is a number. For example: S01.",
    )
    full_code = models.CharField(blank=True, editable=False, max_length=7)
    vehicle_family = models.ForeignKey(
        VehicleFamily,
        null=False,
        blank=False,
        related_name="subassemblies",
        related_query_name="subassembly",
        on_delete=models.CASCADE,
    )
    assembly = ChainedForeignKey(
        Assembly,
        chained_field="vehicle_family",
        chained_model_field="vehicle_family",
        related_name="subassemblies",
        related_query_name="subassembly",
        show_all=False,
        auto_choose=True,
        sort=True,
        verbose_name=_('Parent Assembly'),
    )

    class Meta:
        verbose_name = "subassembly"
        verbose_name_plural = "subassemblies"
        constraints = [
            models.UniqueConstraint(
                fields=["assembly", "code"], name="unique_assembly_subassembly"
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "assembly",
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
                    "full_code",
                ]
            ),
        ]

    def save(self, *args, **kwargs):
        self.full_code = str(self.assembly.code) + self.code
        super(Subassembly, self).save(*args, **kwargs)

    def __str__(self):
        return "[{}] {}".format(self.code, self.name)

    def validate_import_comparison(subassembly, subassembly_to_validate):
        """Compares two subassemblies, returning differences in set of str, when the second entity has non-empty contents that differ with the first."""
        differing_fields = []

        differing_fields.extend(
            compare_entity_field(subassembly, subassembly_to_validate, "name")
        )

        return differing_fields


def get_subassembly_str(code: str="", name: str="") -> str:
    """Returns __str__ representation without an instance."""
    return "[{}] {}".format(code, name)
