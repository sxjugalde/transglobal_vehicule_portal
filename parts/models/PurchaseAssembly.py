from __future__ import annotations

from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.db import transaction
from django.contrib import admin
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from utils.models.AuditableModel import AuditableModel
from utils.logic.compare_entity_field import compare_entity_field

from .Part import Part


@deconstructible
class PurchaseAssembly(AuditableModel):
    """A grouping of several parts, used to unify and sell them as a unit to the customer."""

    PREFIX = "A"

    def get_next_purchase_assembly_code():
        """Get's the next increment for the purchase assembly code, based on the currently highest code + 1."""
        highest_code_pa = PurchaseAssembly.objects.order_by("-code").first()
        if not highest_code_pa:
            return 1000201
        else:
            return highest_code_pa.code + 1

    code = models.PositiveIntegerField(
        _('Purchase Assy #'),
        null=False,
        blank=False,
        unique=True,
        default=get_next_purchase_assembly_code,
        validators=[
            RegexValidator(
                regex=r"^\d{7}$",
                message="Code has to be 7 digits long.",
                code="nomatch",
            ),
        ],
        help_text="PA code without the A prefix.",
    )
    parts = models.ManyToManyField(
        Part,
        related_name="purchase_assemblies",
        related_query_name="purchase_assembly",
        through="PurchaseAssemblyPart",
    )
    parts_contained = models.TextField(blank=True, editable=False)
    full_code = models.CharField(blank=True, editable=False, max_length=8)

    class Meta:
        verbose_name = "purchase assembly"
        verbose_name_plural = "purchase assemblies"
        indexes = [
            models.Index(
                fields=[
                    "code",
                ]
            ),
            models.Index(
                fields=[
                    "full_code",
                ]
            ),
        ]

    def save(self, *args, **kwargs):
        self.full_code = self.PREFIX + str(self.code)
        super(PurchaseAssembly, self).save(*args, **kwargs)
        # Update parts_contained after commiting transaction so parts are referenced correctly.
        transaction.on_commit(self.update_parts_contained)

    def update_parts_contained(self):
        """Updates the parts_contained field in the purchase assembly after it's saved."""
        parts = self.parts.values_list("full_code", flat=True).order_by("full_code")
        parts_str = "-".join(parts)

        if parts_str and parts_str != self.parts_contained:
            self.parts_contained = parts_str
            self.save()

    def __str__(self):
        return self.full_code


def get_all_purchase_assemblies():
    return PurchaseAssembly.objects.order_by("full_code").all()


def get_purchase_assembly_by_id(id: int):
    return PurchaseAssembly.objects.prefetch_related("parts").filter(id=id).first()
