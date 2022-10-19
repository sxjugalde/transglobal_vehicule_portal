from django.db import models
from django.core.validators import ValidationError

from utils.models.AuditableModel import AuditableModel
from utils.logic.compare_entity_field import compare_entity_field
from companies.models.Company import Company

from .Part import Part


class PartSupplier(AuditableModel):
    """A part belonging to a purchase assembly."""

    part = models.ForeignKey(
        Part,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    company = models.ForeignKey(
        Company,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        help_text="Supplier company.",
    )
    supplier_part_number = models.TextField(blank=True)
    purchase_comments = models.TextField(blank=True)

    class Meta:
        verbose_name = "part supplier"
        verbose_name_plural = "part suppliers"

    def __str__(self):
        return f"{self.part} - {self.company}"

    def clean(self):
        if not self.company.is_supplier:
            raise ValidationError("The company assigned must be a supplier.")

    def validate_import_comparison(part_supplier, part_supplier_to_validate):
        """Compares two part suppliers, returning differences in set of str, when the second entity has non-empty contents that differ with the first."""
        differing_fields = []

        differing_fields.extend(
            compare_entity_field(
                part_supplier, part_supplier_to_validate, "supplier_part_number"
            )
        )
        differing_fields.extend(
            compare_entity_field(
                part_supplier, part_supplier_to_validate, "purchase_comments"
            )
        )

        return differing_fields
