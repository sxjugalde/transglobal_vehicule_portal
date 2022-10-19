from django.db import models
from django.core.validators import (
    MinValueValidator,
    ValidationError,
)

from .BOM import BOM
from .Assembly import Assembly
from .Subassembly import Subassembly
from utils.models.AuditableModel import AuditableModel
from parts.models.Part import Part
from parts.models.PurchaseAssemblyPart import PurchaseAssemblyPart


class BOMRow(AuditableModel):
    """Row belonging to a BOM. Defines an individual part or purchase assembly part and where it's located inside a BOM."""

    quantity = models.PositiveSmallIntegerField(
        null=False,
        blank=False,
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Amount used in the BOM in this location.",
    )
    bom = models.ForeignKey(
        BOM,
        null=False,
        blank=False,
        related_name="rows",
        related_query_name="row",
        on_delete=models.CASCADE,
    )
    assembly = models.ForeignKey(
        Assembly,
        null=False,
        blank=False,
        related_name="bom_rows",
        related_query_name="bom_row",
        on_delete=models.PROTECT,
    )
    subassembly = models.ForeignKey(
        Subassembly,
        null=True,
        blank=True,
        related_name="bom_rows",
        related_query_name="bom_row",
        on_delete=models.PROTECT,
    )
    part = models.ForeignKey(
        Part,
        null=True,
        blank=True,
        related_name="bom_rows",
        related_query_name="bom_row",
        on_delete=models.PROTECT,
    )
    purchase_assembly_part = models.ForeignKey(
        PurchaseAssemblyPart,
        null=True,
        blank=True,
        related_name="bom_rows",
        related_query_name="bom_row",
        on_delete=models.PROTECT,
    )

    def clean(self):
        super(BOMRow, self).clean()
        if (self.part is None and self.purchase_assembly_part is None) or (
            self.part is not None and self.purchase_assembly_part is not None
        ):
            raise ValidationError(
                "Either part or purchase assembly part must be populated, but not both."
            )

    class Meta:
        verbose_name = "Bill of materials row"
        verbose_name_plural = "Bill of materials rows"

    def __str__(self):
        part_str = str(self.part or "")
        purchase_assembly_part_str = str(self.purchase_assembly_part or "")
        return " - ".join(
            [
                str(self.assembly),
                str(self.subassembly or ""),
                str(self.quantity) + "u",
                part_str if part_str else purchase_assembly_part_str,
            ]
        )
