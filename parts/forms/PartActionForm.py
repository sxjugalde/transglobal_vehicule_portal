from django import forms
from django.core.exceptions import ValidationError

from django.db import transaction

from ..widgets.ReplacementWidget import ReplacementWidget
from ..models.Part import Part
from vehicles.models.BOMRow import BOMRow


class ReplaceActionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        part = kwargs.pop("part", None)
        super().__init__(*args, **kwargs)
        self.fields["replacement"].queryset = Part.objects.exclude(pk=part.pk).order_by(
            "full_code"
        )
        self.no_integrations = True
        for bomrow in BOMRow.objects.filter(part=part):
            name = f"{bomrow.bom}"
            self.fields[name] = forms.ModelMultipleChoiceField(
                queryset=BOMRow.objects.filter(part=part).filter(bom=bomrow.bom),
                widget=ReplacementWidget(attrs={"style": "vertical-align: middle"}),
                label=name,
                required=False,
            )
            self.field_order = self.field_order + (name,)
            self.no_integrations = False

    @property
    def no_integrations(self) -> bool:
        return self.__no_integrations

    @no_integrations.setter
    def no_integrations(self, no_integrations: bool):
        self.__no_integrations = no_integrations

    def clean(self):
        cleaned_data = super().clean()

        empty_selection = True
        for field_name, field_data in cleaned_data.items():
            if field_name != "replacement" and field_data:
                empty_selection = False
                break

        if empty_selection:
            raise ValidationError(
                "Please select at least one BOM integration to replace."
            )

    def save(self, part, user):
        try:
            self.form_action(part, user)
        except Exception as e:
            error_message = str(e)
            self.add_error(None, error_message)
            raise

    replacement = forms.ModelChoiceField(queryset=None, initial=0)

    field_order = ("replacement",)

    def form_action(self, part, user):
        bomkeys = filter(lambda x: x != "replacement", self.cleaned_data.keys())
        with transaction.atomic():
            for k in bomkeys:
                for bomrow in self.cleaned_data[k]:
                    bomrow.part = self.cleaned_data["replacement"]
                    bomrow.save()
