from django import forms
from .models import Expense


class ExpenseSearchForm(forms.ModelForm):
    _MIN_YEAR, _MAX_YEAR = 1980, 2020
    from_date = forms.DateField(required=False, widget=forms.SelectDateWidget(years=range(_MIN_YEAR, _MAX_YEAR + 1)))
    to_date = forms.DateField(required=False, widget=forms.SelectDateWidget(years=range(_MAX_YEAR, _MIN_YEAR - 1, -1)))

    class Meta:
        model = Expense
        fields = ('name', 'from_date', 'to_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False
