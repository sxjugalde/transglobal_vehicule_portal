from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")

    def clean(self):
        cleaned_data = super(CustomUserChangeForm, self).clean()
        error_list = []

        if self.instance.id:
            is_staff = cleaned_data.get("is_staff")
            company = cleaned_data.get("company")

            if not is_staff and not company:
                self.add_error(
                    "company",
                    "A customer user must have a company assigned.",
                )
