from django import forms
from django.core.exceptions import ValidationError

from ..logic.AssemblyLogic import (
    get_all_assembly_subassembly_locations_by_vehicle_family,
)
from parts.models.PurchaseAssembly import get_all_purchase_assemblies


class SelectPartLocationForm(forms.Form):
    """Used to select locations inside a formset for each part in the PA."""

    def __init__(self, part_location_choices, *args, **kwargs):
        super(SelectPartLocationForm, self).__init__(*args, **kwargs)
        self.set_part_location_choices(choices=part_location_choices)

    pa_part_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    part_location = forms.ChoiceField(
        label="Where should it be placed?", required=True
    )  # This will be changes /W JS.

    def set_part_location_choices(self, choices):
        self.fields["part_location"].choices = choices


class AddBOMRowPurchaseAssemblyForm(forms.Form):
    # Fields
    pa_to_add = forms.ChoiceField(
        label="Which purchase assembly should be added?",
        widget=forms.Select(
            attrs={"id": "pa_to_add"}
        ),  # ID is used to select them /w JQuery.
        required=True,
    )

    def load_purchase_assembly_choices(self):
        blank_choice = (-1, "---------")
        purchase_assemblies = list(
            map(lambda x: (x.pk, str(x)), tuple(get_all_purchase_assemblies()))
        )
        purchase_assemblies.insert(0, blank_choice)
        self.fields["pa_to_add"].choices = purchase_assemblies

    def clean_pa_to_add(self):
        data = self.cleaned_data["pa_to_add"]

        if data == "-1":
            raise ValidationError("Please select an appropiate purchase assembly.")

        return data
