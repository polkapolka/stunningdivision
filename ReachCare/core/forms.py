from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms import layout


class LoginForm(forms.Form):
    phone = forms.CharField(label="Phone Number", max_length=500)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = layout.Layout(
            layout.Field('phone'),
            layout.Submit()

        )