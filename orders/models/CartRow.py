from django.db import models
from django.core.validators import ValidationError, MinValueValidator

from .Cart import Cart
from vehicles.models.Vehicle import Vehicle
from vehicles.models.BOMRow import BOMRow
from utils.models.AuditableModel import AuditableModel


class CartRow(AuditableModel):
    """A cart row entry inputted by a customer user. References a BOMRow (among other things), and stores a log of information."""

    cart = models.ForeignKey(
        Cart,
        null=False,
        blank=False,
        related_name="rows",
        related_query_name="row",
        on_delete=models.CASCADE,
    )
    vehicle = models.ForeignKey(
        Vehicle,
        null=True,
        blank=True,
        related_name="cart_rows",
        related_query_name="cart_row",
        on_delete=models.SET_NULL,
    )
    bom_row = models.ForeignKey(
        BOMRow,
        null=True,
        blank=True,
        related_name="cart_rows",
        related_query_name="cart_row",
        on_delete=models.SET_NULL,
    )
    quantity = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=1,
        validators=[
            MinValueValidator(1),
        ],
    )
    # Historic log fields.
    vehicle_identification_number = models.CharField(
        blank=True, default="", max_length=20
    )
    vehicle_nickname = models.CharField(blank=True, default="", max_length=120)
    bom_name = models.CharField(blank=True, default="", max_length=75)  # Unused.
    bom_code = models.CharField(blank=True, default="", max_length=25)  # Unused.
    bom_revision = models.CharField(blank=True, default="", max_length=5)  # Unused.
    assembly_name = models.CharField(blank=True, default="", max_length=75)  # Unused.
    assembly_code = models.CharField(blank=True, default="", max_length=5)
    subassembly_name = models.CharField(
        blank=True, default="", max_length=75
    )  # Unused.
    subassembly_full_code = models.CharField(blank=True, default="", max_length=10)
    purchase_assembly_full_code = models.CharField(
        blank=True, default="", max_length=10
    )
    part_name = models.CharField(blank=True, default="", max_length=200)
    part_full_code = models.CharField(blank=True, default="", max_length=15)
    part_uses = models.CharField(blank=True, default="", max_length=3)

    class Meta:
        verbose_name = "cart row"
        verbose_name_plural = "cart rows"
        indexes = [
            models.Index(
                fields=[
                    "cart",
                ]
            ),
            models.Index(fields=["cart", "vehicle", "bom_row"]),
        ]

    def __str__(self):
        return "{} - {}{} - [{}][{}] - {} {} - {}u - {} - {}".format(
            self.vehicle_identification_number,
            self.bom_code,
            self.bom_revision,
            self.assembly_code,
            self.subassembly_full_code,
            self.purchase_assembly_full_code,
            self.part_name,
            self.part_uses,
            self.created_by,
            self.created_on,
        )

    def clean(self):
        if not self.vehicle:
            raise ValidationError("The cart row's Vehicle is required on create.")
        if not self.bom_row:
            raise ValidationError("The cart row's BOMRow is required on create.")

    def save(self, *args, **kwargs):
        # Fetch vehicle and BOMRow information.
        vehicle = Vehicle.objects.select_related("bom").get(id=self.vehicle.id)
        bom_row = (
            BOMRow.objects.select_related("assembly")
            .select_related("subassembly")
            .select_related("part")
            .select_related("purchase_assembly_part")
            .select_related("purchase_assembly_part__purchase_assembly")
            .select_related("purchase_assembly_part__part")
        ).get(id=self.bom_row.id)

        # Set values
        self.vehicle_identification_number = vehicle.identification_number
        self.vehicle_nickname = vehicle.nickname
        self.bom_name = vehicle.bom.name
        self.bom_code = vehicle.bom.code
        self.bom_revision = vehicle.bom.revision

        self.assembly_code = bom_row.assembly.code
        self.assembly_name = bom_row.assembly.name
        self.subassembly_full_code = bom_row.subassembly.full_code
        self.subassembly_name = bom_row.subassembly.name

        if bom_row.part:
            # It's a part.
            self.part_full_code = bom_row.part.full_code
            self.part_name = bom_row.part.name
            self.part_uses = bom_row.quantity
        elif bom_row.purchase_assembly_part:
            # It's a PA.
            self.purchase_assembly_full_code = (
                bom_row.purchase_assembly_part.purchase_assembly.full_code
            )
            self.part_full_code = bom_row.purchase_assembly_part.part.full_code
            self.part_name = bom_row.purchase_assembly_part.part.name
            self.part_uses = bom_row.purchase_assembly_part.quantity

        super(CartRow, self).save(*args, **kwargs)
