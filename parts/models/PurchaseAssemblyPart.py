from __future__ import annotations

from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.contrib import admin

from utils.logic.compare_entity_field import compare_entity_field

from .Part import Part
from .PurchaseAssembly import PurchaseAssembly

from django.utils.deconstruct import deconstructible


@deconstructible
class PurchaseAssemblyPart(models.Model):
    """A part belonging to a purchase assembly."""

    part = models.ForeignKey(
        Part,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    purchase_assembly = models.ForeignKey(
        PurchaseAssembly,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveSmallIntegerField(
        null=False,
        blank=False,
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Amount used in the purchase assembly.",
    )
    full_code = models.CharField(
        blank=True,
        editable=False,
        max_length=20,
    )

    class Meta:
        verbose_name = "purchase assembly part"
        verbose_name_plural = "purchase assembly parts"
        indexes = [
            models.Index(
                fields=[
                    "purchase_assembly",
                ]
            ),
            models.Index(
                fields=[
                    "purchase_assembly",
                    "part",
                    "quantity",
                ]
            ),
            models.Index(
                fields=[
                    "full_code",
                ]
            ),
        ]

    def save(self, *args, **kwargs):
        self.full_code = "-".join(
            [
                str(self.purchase_assembly.full_code),
                self.part.full_code,
                str(self.quantity),
            ]
        )
        super(PurchaseAssemblyPart, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_code

    def validate_import_comparison(
        purchase_assembly_part, purchase_assembly_part_to_validate
    ):
        """Compares two purchase_assembly_parts, returning differences in set of str, when the second entity has non-empty contents that differ with the first."""
        differing_fields = []

        differing_fields.extend(
            compare_entity_field(
                purchase_assembly_part, purchase_assembly_part_to_validate, "quantity"
            )
        )

        return differing_fields


def get_purchase_assembly_part_verbose_str(
    purchase_assembly_full_code: int,
    part_full_code: str = "",
    part_name: str = "",
    quantity: int = 1,
) -> str:
    """Returns a more readable version of the entity's str representation, without an instance."""
    return "[{}] [{}] [{}] {}".format(
        str(purchase_assembly_full_code),
        "P" + part_full_code,
        "Uses " + str(quantity),
        part_name,
    )


def get_all_purchase_assembly_parts(purchase_assembly_id: int):
    return (
        PurchaseAssemblyPart.objects.select_related("part")
        .filter(purchase_assembly_id=purchase_assembly_id)
        .order_by("full_code")
        .all()
    )
