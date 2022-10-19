from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import ValidationError
from django.db import models

from utils.models.AuditableModel import AuditableModel
from companies.models.Company import Company


class CustomUser(AbstractUser, AuditableModel):
    email = models.EmailField(blank=False)
    email_confirmed = models.BooleanField(default=False)
    confirmation_email_sent = models.BooleanField(default=False)
    company = models.ForeignKey(
        Company, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.username

    def clean(self):
        if self.pk:
            used_email = (
                CustomUser.objects.filter(email=self.email).exclude(pk=self.pk).exists()
            )
            if used_email:
                raise ValidationError(
                    "A user with this email already exists, please input a different one."
                )
