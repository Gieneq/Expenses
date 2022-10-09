from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.list import ListView

from .forms import ExpenseSearchForm
from .models import Expense, Category
from .reports import expenses_summary


def save_filtering_parameters(request, parameters):
    """
    Use to store filtering parameters in request session.
    """
    request.session['filterings'] = parameters.urlencode()


def retrieve_filtering_parameters(request):
    """
    Use to retrieve filtering parameters from session. If it is a new session parameters will be generated.
    Default parameters should fill entire Category Choice Field in the ExpenseSearchForm.
    """
    if 'filterings' in request.session:
        params = request.session['filterings']
    else:
        params = '&'.join(
            f"categories={v}" for v in ExpenseSearchForm.category_choices().keys())
    return params


def filter_expenses_queryset(queryset, params):
    """
    :param queryset: Expenses Queryset,
    :param params: dict of parameters to filter queryset. Can be obtained from ExpenseSearchForm.
    """
    name = params.get('name', '').strip()
    if name:
        queryset = queryset.filter(name__icontains=name)

    from_date, to_date = params.get('from_date'), params.get('to_date')
    if from_date:
        queryset = queryset.filter(date__gte=from_date)

    if to_date:
        queryset = queryset.filter(date__lt=to_date)

    categories = params.get('categories')
    return queryset.filter(category__id__in=categories)


def split_to_parameters_ordering_from(query_params):
    """
    Split query parameters into filtering parameters and ordering (sorting) parameters.
    Page for pagination is removed to prevent repetition.
    """
    parameters = query_params.copy()
    parameters.pop('page', True)

    ordering = query_params.copy()
    ordering.clear()
    if 'order_by' in parameters:
        ordering['order_by'] = parameters.pop('order_by')[0]
    return parameters, ordering


def reverse_with_params(viewname, encoded_params):
    """
    Return reverse with encoded parameters.
    """
    return f"{reverse(viewname)}?{encoded_params}"


class ExpenseListView(ListView):
    model = Expense
    paginate_by = 5

    def get(self, *args, **kwargs):
        query_params = self.request.GET

        # initial filtering query parameters, redirect for apply filter
        if 'categories' not in query_params:
            filtering_params = retrieve_filtering_parameters(self.request)
            return redirect(reverse_with_params('expenses:expense-list', filtering_params))

        return super().get(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        query_params = self.request.GET
        queryset = object_list if object_list is not None else self.object_list

        form = ExpenseSearchForm(query_params)
        if form.is_valid():
            queryset = filter_expenses_queryset(queryset, form.cleaned_data)

        parameters, ordering = split_to_parameters_ordering_from(query_params)
        summary = expenses_summary(queryset)

        save_filtering_parameters(self.request, parameters)
        return super().get_context_data(
            parameters=parameters.urlencode(),
            ordering=ordering.urlencode(),
            form=form,
            object_list=queryset,
            summary_per_category=summary['per_category'],
            summary_per_year_month=summary['per_year_month'],
            total_amount_spent=summary['total'],
            **kwargs)

    def get_ordering(self):
        order_by = self.request.GET.get('order_by', '')
        return order_by


class CategoryListView(ListView):
    model = Category
    paginate_by = 5
