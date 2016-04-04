from django import forms
from events.models import EventSignupEntry

from datetime import timedelta


def date_range(first_day, last_day):
    for i in range(int((last_day - first_day)).days):
        yield first_day + timedelta(i)


class DateInput(forms.TextInput):
    input_type = 'date'


class EventRegistration(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.event_name = kwargs.pop('name')
        self.event_skus = kwargs.pop('skus')
        self.event_begin = kwargs.pop('event_begin')
        self.event_end = kwargs.pop('event_end')

        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        first_day = self.fields['arrival']
        last_day = self.fields['departure']

        pre_stay_days = self._days_before_event(first_day)
        post_stay_days = self._days_after_event(last_day)

        course_days = list(
            date_range(
                first_day + timedelta(pre_stay_days),
                # one extra day for inclusive date range
                last_day - timedelta(post_stay_days - 1)
            )
        )

        items = []
        total = 0

        for sku in self._sort_single_dated_skus_by_duration():
            if self._fits(sku, course_days):
                cost, item = self._create_paypal_item(sku, 1)
                items.append(item)
                total += cost
                course_days = self._remove_sku_days(sku, course_days)

        flat_rate_day_sku = self.event_skus.filter(flat_rate_day=True)

        if course_days and flat_rate_day_sku:
            cost, item = self._create_paypal_item(flat_rate_day_sku,
                                                  len(course_days))
            items.append(item)
            total += cost

        self.fields['paypal_transactions'] = {
            'item_list': items,
            'amount': {'total': total, 'currency': 'NOK'}
        }

        super().save(*args, **kwargs)

    def _remove_sku_days(self, sku, course_days):
        # add one day for inclusive date range
        sku_dates = list(date_range(sku.first_day, sku.last_day + timedelta(1)))
        return [day for day in course_days if day not in sku_dates]

    def _create_paypal_item(self, sku, quantity):
        return (
            sku.price,
            dict(
                name='{} - {}'.format(self.event_name, sku.name),
                sku=sku.course_code,
                price='{}.00'.format(str(sku.price)),
                currency='NOK',
                quantity=str(quantity),
            ),
        )

    def _fits(self, sku, course_days):
        return (course_days[0] >= sku.first_day and
                course_days[-1] <= sku.last_day)

    def _days_before_event(self, first_day):
        return max(int((self.event_begin - first_day).days), 0)

    def _days_after_event(self, last_day):
        return max(int((last_day - self.event_end).days), 0)

    def _sort_single_dated_skus_by_duration(self):
        def sort_func(x):
            return (not x.multi_itemed and
                    max(int((x.departure - x.arrival).days)))

        return sorted(self.event_skus, key=sort_func)

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
