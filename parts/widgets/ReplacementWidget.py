from django import forms


class ReplacementWidget(forms.CheckboxSelectMultiple):
    template_name = "widget/parts_choice_replace.html"
