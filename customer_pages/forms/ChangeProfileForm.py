from django import forms
from django.core.validators import ValidationError
from django.contrib.auth import get_user_model


class ChangeProfileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["first_name"].initial = self.user.first_name
            self.fields["last_name"].initial = self.user.last_name
            self.fields["email"].initial = self.user.email

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
        max_length=30,
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
        max_length=30,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"}), max_length=254
    )

    def clean(self):
        email = self.cleaned_data["email"]
        if email:
            used_email = (
                get_user_model()
                .objects.filter(email=email)
                .exclude(pk=self.user.pk)
                .exists()
            )
            if used_email:
                raise ValidationError(
                    "A user with this email already exists, please use a different one."
                )

    def save(self, user):
        try:
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.email = self.cleaned_data["email"]
            user.save()
        except Exception as e:
            error_message = str(e)
            self.add_error(None, error_message)
            raise
