from collections import OrderedDict
from functools import reduce

from django.db.models import Sum, Value, Q, F, Count
from django.db.models.functions import Coalesce, TruncMonth, TruncYear, ExtractYear, ExtractMonth


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


def summary_per_year_month(queryset):
    result_qs = queryset.annotate(year=Coalesce('date__year', Value(0)),
                                  month=Coalesce('date__month', Value(0))).order_by()
    result_qs = result_qs.values('year', 'month').annotate(total=Sum('amount'))
    result_qs = result_qs.values_list('year', 'month', 'total')

    result = dict()
    for year, month, total in result_qs:
        result.setdefault(year, []).append((month, total))

    result = OrderedDict(sorted(
        ((year, {'total': reduce(lambda a, b: a + b[1], months_totals, 0), 'months': months_totals}) for
         year, months_totals in result.items()), key=lambda x: x[0]))

    return result


def summary_per_year(queryset):
    return OrderedDict(
        sorted(queryset.annotate(year=Coalesce('date__year', Value(0))).order_by().values('year').annotate(
            s=Sum('amount')).values_list('year', 's')))
