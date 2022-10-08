from collections import OrderedDict
from functools import reduce

from django.db.models import Sum, Value
from django.db.models.functions import Coalesce


def summary_per_category(queryset):
    return OrderedDict(sorted(
        queryset
        .annotate(category_name=Coalesce('category__name', Value('-')))
        .order_by()
        .values('category_name')
        .annotate(s=Sum('amount'))
        .values_list('category_name', 's')
    ))


def total_amount_spent(summary_dict):
    return sum(summary_dict.values())


# optional on queryset. Evaluating using precalculated OrderedDict should be faster.
def total_amount_spent_qs(queryset):
    return queryset.aggregate(total_amount_spent=Sum('amount'))['total_amount_spent']
