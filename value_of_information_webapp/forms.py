from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


class EmptyForm(forms.Form):
    favorite_number = forms.FloatField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_parameters'
        self.helper.add_input(Submit('submit', 'Submit'))
