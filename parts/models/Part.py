from __future__ import annotations

from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, ValidationError
from django.contrib import admin
from django.db.models import Q
from django.apps import apps
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from companies.models.Company import Company
from utils.models.AuditableModel import AuditableModel
from utils.logic.compare_entity_field import compare_entity_field


@deconstructible
class Part(AuditableModel):
    """A unique part, the smallest unit used to build vehicles and assemblies."""

    IS_PURCHASED_IMPORT_VALUE = "Purchase"
    IS_FABRICATED_IMPORT_VALUE = "Fab"

    def get_next_part_code():
        """Get's the next increment for the part code, based on the currently highest code + 1."""
        highest_code_part = Part.objects.order_by("-code").first()
        if not highest_code_part:
            return 20001
        else:
            return highest_code_part.code + 1

    name = models.CharField(_('Part Name'), blank=False, max_length=150)
    code = models.PositiveIntegerField(
        _('Part #'),
        null=False,
        blank=False,
        default=get_next_part_code,
        validators=[
            RegexValidator(
                regex=r"^\d{5}$",
                message="Code has to be 5 digits long.",
                code="nomatch",
            ),
        ],
        help_text="5 digit TG code.",
    )
    suffix = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Subcomponent suffix.",
    )
    revision = models.CharField(
        blank=True,
        max_length=1,
        help_text="Revision code. For example: A.",
    )
    suppliers = models.ManyToManyField(
        Company,
        related_name="parts",
        related_query_name="part",
        through="PartSupplier",
    )
    notes = models.TextField(blank=True)
    dimension = models.TextField(blank=True)
    material = models.TextField(blank=True)
    is_purchased = models.BooleanField(default=False)
    is_obsolete = models.BooleanField(default=False)
    full_code = models.CharField(blank=True, unique=True, editable=False, max_length=10)

    class Meta:
        verbose_name = "part"
        verbose_name_plural = "parts"
        constraints = [
            models.UniqueConstraint(
                fields=["code", "suffix", "revision"], name="unique_part_identification"
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "full_code",
                ]
            ),
        ]

    def clean(self):
        if not self.id:
            existing_part = Part.objects.filter(
                code=self.code, suffix=self.suffix, revision=self.revision
            ).first()
            if existing_part:
                raise ValidationError(
                    "A Part with this code, suffix and revision already exists."
                )

        if self.is_obsolete:
            # Dinamically obtain model to avoid circular reference.
            BOMRow = apps.get_model(app_label="vehicles", model_name="BOMRow")
            is_used = BOMRow.objects.filter(
                Q(part=self) | Q(purchase_assembly_part__part=self)
            ).exists()
            if is_used:
                raise ValidationError(
                    "A Part can't be marked as obsolete while being used in a BOM, either directly or through a purchase assembly."
                )

    def save(self, *args, **kwargs):
        self.full_code = str(self.code) + str(self.suffix or "") + self.revision
        super(Part, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_code + " - " + self.name

    def validate_import_comparison(part, part_to_validate):
        """Compares two parts, returning differences in set of str, when the second entity has non-empty contents that differ with the first."""
        differing_fields = []

        differing_fields.extend(compare_entity_field(part, part_to_validate, "name"))
        differing_fields.extend(
            compare_entity_field(part, part_to_validate, "material")
        )
        differing_fields.extend(
            compare_entity_field(
                part, part_to_validate, "is_purchased", "is it purchased?"
            )
        )
        differing_fields.extend(
            compare_entity_field(
                part, part_to_validate, "revision_notes", "revision notes"
            )
        )
        differing_fields.extend(
            compare_entity_field(part, part_to_validate, "dimension")
        )
        differing_fields.extend(
            compare_entity_field(part, part_to_validate, "comments")
        )
        differing_fields.extend(
            compare_entity_field(
                part, part_to_validate, "is_available", "is it available?"
            )
        )

        return differing_fields
