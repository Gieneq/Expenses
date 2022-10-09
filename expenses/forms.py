from collections import OrderedDict

from django import forms
from .models import Expense, Category


class ExpenseSearchForm(forms.ModelForm):
    _MIN_YEAR, _MAX_YEAR = 1980, 2020  # TODO better make tuple and reverse range

    from_date = forms.DateField(required=False, widget=forms.SelectDateWidget(years=range(_MIN_YEAR, _MAX_YEAR + 1)))
    to_date = forms.DateField(required=False, widget=forms.SelectDateWidget(years=range(_MAX_YEAR, _MIN_YEAR - 1, -1)))
    categories = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Expense
        fields = ('name', 'from_date', 'to_date', 'categories')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['categories'].choices = ExpenseSearchForm.category_choices().items()

    @staticmethod
    def category_choices():
        return OrderedDict([(category.id, category.name) for category in Category.objects.order_by('name')])
