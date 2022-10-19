from django.db import models
from django.core.validators import ValidationError

from utils.models.AuditableModel import AuditableModel
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Company(AuditableModel):
    """A company, which could be a customer or supplier."""

    name = models.CharField(blank=False, unique=True, max_length=100)
    is_supplier = models.BooleanField(null=False, blank=False, default=False)
    is_customer = models.BooleanField(null=False, blank=False, default=False)
    logo = models.ImageField(
        _('Logo'),
        upload_to='company_logos',
        blank=True,
        null=True,
        )

    class Meta:
        verbose_name = "company"
        verbose_name_plural = "companies"
        indexes = [
            models.Index(
                fields=[
                    "is_supplier",
                ]
            ),
            models.Index(
                fields=[
                    "is_customer",
                ]
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if not self.id:
            # Make case-insensitive lookup.
            existing_company = Company.objects.filter(name__iexact=self.name).first()
            if existing_company:
                raise ValidationError(
                    "A Company with this name already exists. Please review case sensitivity."
                )
        elif not self.is_supplier and self.parts.exists():
            raise ValidationError(
                "This Company supplies parts, so it has to be marked as a supplier."
            )
