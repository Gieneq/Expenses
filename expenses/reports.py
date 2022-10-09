from collections import OrderedDict
from functools import reduce

from django.db.models import Sum, Value
from django.db.models.functions import Coalesce


def to_ordered_dict(it_of_tuples):
    """Converts and sorts list of tuples to OrderedDict.
    Regular dict should be fine, since Python 3.7 it preserves insertion order."""
    return OrderedDict(sorted(it_of_tuples))


def summary_per_category(queryset):
    return to_ordered_dict(
        queryset
        .annotate(category_name=Coalesce('category__name', Value('-')))
        .order_by()
        .values('category_name')
        .annotate(s=Sum('amount'))
        .values_list('category_name', 's')
    )


def total_amount_spent_using_dict(summary_dict):
    """
    Returns summary of all Expenses based on result of summary_per_category function (should be faster).
    See total_amount_spent for queryset based alternative.
    """
    return sum(summary_dict.values())


def total_amount_spent(queryset):
    """
    Returns summary of all Expenses based on Expenses queryset.
    """
    return queryset.aggregate(total_amount_spent=Sum('amount'))['total_amount_spent']


def summary_per_year_month(queryset):
    """
    Returns OrderedDict of key-value pairs:
    {year: {'total': amount spent per year, 'months' : list of months numbers like [1,3,12]}}
    """
    result_qs = queryset.annotate(year=Coalesce('date__year', Value(0)),
                                  month=Coalesce('date__month', Value(0))).order_by()
    result_qs = result_qs.values('year', 'month').annotate(total=Sum('amount'))
    result_qs = result_qs.values_list('year', 'month', 'total')

    result = dict()
    for year, month, total in result_qs:
        result.setdefault(year, []).append((month, total))

    result = to_ordered_dict(
        ((year, {'total': reduce(lambda a, b: a + b[1], months_totals, 0), 'months': months_totals}) for
         year, months_totals in result.items()))

    return result


def summary_per_year(queryset):
    """
    Returns OrderedDict of key-value pairs: {year: amount spent per year}.
    """
    return to_ordered_dict(queryset.annotate(year=Coalesce('date__year', Value(0))).order_by().values('year').annotate(
        s=Sum('amount')).values_list('year', 's'))


def expenses_summary(queryset):
    """
    Return summary of expenses
    :param queryset: prefiltered queryset of Expenses.
    :return: dict of summaries: per_year_month, per_category, total.
    """
    s_per_categories = summary_per_category(queryset)
    return {
        'per_year_month': summary_per_year_month(queryset),
        'per_category': s_per_categories,
        'total': total_amount_spent_using_dict(s_per_categories)
    }
