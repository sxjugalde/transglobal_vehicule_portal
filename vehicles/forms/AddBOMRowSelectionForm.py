from django import forms


class AddBOMRowSelectionForm(forms.Form):
    # Fields
    SELECTION_CHOICES = [("part", "Part"), ("purchase_assembly", "Purchase Assembly")]

    # TODO: Improve - Try to use select2 widget, to facilitate UX.
    part_or_pa_selection = forms.ChoiceField(
        label="Add a part or purchase assembly?",
        choices=SELECTION_CHOICES,
        widget=forms.RadioSelect(
            attrs={"id": "part_or_pa_selection"}
        ),  # ID is used to select them /w JQuery.
        required=True,
    )
