from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.list import ListView

from .forms import ExpenseSearchForm
from .models import Expense, Category
from .reports import summary_per_category, total_amount_spent, summary_per_year_month


class ExpenseListView(ListView):
    model = Expense
    paginate_by = 5

    def get(self, *args, **kwargs):
        query_params = self.request.GET
        if 'categories' not in query_params:
            if 'filterings' in self.request.session:
                # retrieve from session
                filtering_query_params = self.request.session['filterings']
            else:
                filtering_query_params = '&'.join(
                    f"categories={v}" for v in ExpenseSearchForm.category_choices().keys())
            return redirect(reverse('expenses:expense-list') + f'?{filtering_query_params}')

        return super().get(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        query_params = self.request.GET.copy()
        queryset = object_list if object_list is not None else self.object_list

        form = ExpenseSearchForm(query_params)
        if form.is_valid():
            cdata = form.cleaned_data
            print('-->', cdata)

            # Filtering
            name = cdata.get('name', '').strip()
            if name:
                queryset = queryset.filter(name__icontains=name)

            from_date, to_date = cdata.get('from_date'), cdata.get('to_date')
            if from_date:
                queryset = queryset.filter(date__gte=from_date)

            if to_date:
                queryset = queryset.filter(date__lt=to_date)

            categories = cdata.get('categories')
            queryset = queryset.filter(category__id__in=categories)

        parameters = query_params.copy()
        parameters.pop('page', True)

        ordering = query_params.copy()
        ordering.clear()
        if 'order_by' in parameters:
            ordering['order_by'] = parameters.pop('order_by')[0]

        summary_ym = summary_per_year_month(queryset)
        summary = summary_per_category(queryset)
        self.request.session['filterings'] = parameters.urlencode()
        return super().get_context_data(
            parameters=parameters.urlencode(),
            ordering=ordering.urlencode(),
            form=form,
            object_list=queryset,
            summary_per_category=summary,
            summary_per_year_month=summary_ym,
            total_amount_spent=total_amount_spent(summary),
            **kwargs)

    def get_ordering(self):
        order_by = self.request.GET.get('order_by', '')
        return order_by


class CategoryListView(ListView):
    model = Category
    paginate_by = 5
