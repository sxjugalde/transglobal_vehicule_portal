from django import forms
from django.core.validators import ValidationError

from functools import partial

from vehicles.logic.BOMLogic import get_all_boms

DateInput = partial(forms.DateInput, {"class": "datepicker"})


class MostRequestedPartsReportForm(forms.Form):
    from_date = forms.DateField(widget=DateInput())
    to_date = forms.DateField(widget=DateInput())
    count = forms.IntegerField(
        min_value=10, max_value=100, initial=10, label="How many rows?"
    )
    bom = forms.ChoiceField(label="Filter by BOM?", required=False)

    def load_bom_choices(self):
        blank_choice = (None, "---------")
        boms = list(map(lambda x: (x.pk, str(x)), tuple(get_all_boms())))
        boms.insert(0, blank_choice)
        self.fields["bom"].choices = boms
