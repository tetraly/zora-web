from django import forms

MODES = (
    ('standard', 'Standard'),
    ('itemonly', 'Item Only'),
)


class GenerateForm(forms.Form):
    seed = forms.Field(required=False)
    mode = forms.ChoiceField(required=False, choices=MODES, initial='open')
    flags = forms.Field(required=False, initial='')
    debug_mode = forms.BooleanField(required=False, initial=False)
    race_mode = forms.BooleanField(required=False, initial=False)
