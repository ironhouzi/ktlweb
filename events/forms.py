from django import forms
from events.models import EventSignupEntry

from datetime import timedelta


def date_range(first_day, last_day):
    for i in range((last_day - first_day).days):
        yield first_day + timedelta(i)


class DateInput(forms.TextInput):
    input_type = 'date'


class EventRegistration(forms.ModelForm):
    def save(self, *args, **kwargs):
        self.event_name = kwargs.pop('name', '')
        self.event_skus = kwargs.pop('skus', None)

        event_begin = kwargs.pop('event_begin', None)
        event_end = kwargs.pop('event_end', None)

        try:
            self.event_begin = event_begin.date()
            self.event_end = event_end.date()
        except AttributeError:
            self.event_begin = event_begin
            self.event_end = event_end

        self._generate_paypal_items()

        super().save(*args, **kwargs)

    def _generate_paypal_items(self):
        participants_first_day = self.cleaned_data['arrival']
        participants_last_day = self.cleaned_data['departure']

        pre_stay_days = self._days_before_event(participants_first_day)
        post_stay_days = self._days_after_event(participants_last_day)

        participants_days = list(
            date_range(
                participants_first_day + timedelta(pre_stay_days),
                # one extra day for inclusive date range
                participants_last_day - timedelta(post_stay_days - 1)
            )
        )

        items = []
        total = 0
        skus = self.event_skus.filter(multi_itemed=False)

        for sku in self.sort_sku_by_start_date_and_duration(skus):
            if self.fits(sku, participants_days):
                cost, item = self.create_paypal_item(self.event_name, sku, 1)
                items.append(item)
                total += cost
                participants_days = self.remove_sku_days(sku, participants_days)

        flat_rate_day_sku = self.event_skus.filter(flat_rate_day=True)

        if participants_days and flat_rate_day_sku:
            cost, item = self.create_paypal_item(self.event_name,
                                                  flat_rate_day_sku,
                                                  len(participants_days))
            items.append(item)
            total += cost

        self.instance.paypal_transactions = {
            'item_list': items,
            'amount': {'total': total, 'currency': 'NOK'}
        }

    def sort_sku_by_start_date_and_duration(self, skus):
        date_sorted_skus = sorted(
            skus,
            key=lambda x: x.first_day
        )

        return sorted(
            date_sorted_skus,
            key=lambda x: (x.last_day - x.first_day).days,
            reverse=True
        )

    def remove_sku_days(self, sku, participants_days):
        # add one day for inclusive date range
        sku_dates = list(date_range(sku.first_day, sku.last_day + timedelta(1)))
        return [day for day in participants_days if day not in sku_dates]

    def create_paypal_item(self, event_name, sku, quantity):
        return (
            sku.price,
            dict(
                name='{} - {}'.format(event_name, sku.name),
                sku=sku.course_code,
                price='{}.00'.format(sku.price),
                currency='NOK',
                quantity=str(quantity),
            ),
        )

    def fits(self, sku, participants_days):
        '''
        Checks if the date range of the SKU fits within the time frame of the
        participants stay.
        '''
        return (participants_days[0] >= sku.first_day and
                participants_days[-1] <= sku.last_day)

    def _days_before_event(self, first_day):
        return max((self.event_begin - first_day).days, 0)

    def _days_after_event(self, last_day):
        return max((last_day - self.event_end).days, 0)

    class Meta:
        model = EventSignupEntry
        fields = [
            'gender', 'first_name', 'sir_name', 'email', 'phone_number',
            'payment', 'discount', 'arrival', 'departure',
        ]
        widgets = {
            'arrival': DateInput(),
            'departure': DateInput(),
        }


class GenericAddressForm(forms.Form):
    country = forms.ChoiceField(
        choices=(('no', 'Norway'), ('uk', 'United Kingdom')),
        initial='no',
        required=True,
    )
