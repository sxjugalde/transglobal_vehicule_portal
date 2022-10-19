from django import forms

from parts.models.Part import Part
from parts.logic.PartLogic import get_all_parts
from ..logic.AssemblyLogic import (
    get_all_assembly_subassembly_locations_by_vehicle_family,
)


class AddBOMRowPartForm(forms.Form):
    # Fields
    part_to_add = forms.ChoiceField(
        label="Which part should be added?",
    )
    part_location = forms.ChoiceField(label="Where should it be placed?")
    part_quantity = forms.IntegerField(
        label="How many are used?", min_value=1, initial=1
    )

    field_order = ("part_to_add", "part_location", "part_quantity")

    # Methods
    def save(self, user, bom_rows):
        try:
            pass
        except Exception as e:
            error_message = str(e)
            self.add_error(None, error_message)
            raise

    def load_part_choices(self):
        self.fields["part_to_add"].choices = map(
            lambda x: (x.pk, str(x)), tuple(get_all_parts())
        )

    def load_part_locations(self, vehicle_family_id: int):
        self.fields[
            "part_location"
        ].choices = get_all_assembly_subassembly_locations_by_vehicle_family(
            vehicle_family_id
        )
