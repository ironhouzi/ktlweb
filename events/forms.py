from django import forms
from events.models import EventSignupEntry


class GenericPersonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        dates = kwargs.pop('dates')

        super().__init__(*args, **kwargs)

        print(dates)
        self.fields['dates'] = forms.ChoiceField(
            choices = (x for x in zip(dates, ('zero', 'one', 'two', 'three'))),
            initial = '0',
            required = False,
        )

    class Meta:
        model = EventSignupEntry
        fields = [
            'gender', 'first_name', 'sir_name',
            'email', 'phone_number', 'payment', 'discount'
        ]


class GenericAddressForm(forms.Form):
    country = forms.ChoiceField(
        choices = (('no', 'Norway'), ('uk', 'United Kingdom')),
        initial = 'no',
        required = True,
    )
