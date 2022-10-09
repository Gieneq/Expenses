from django.http import QueryDict
from django.views.generic.list import ListView

from .forms import ExpenseSearchForm
from .models import Expense, Category
from .reports import summary_per_category, total_amount_spent, summary_per_year_month


class ExpenseListView(ListView):
    model = Expense
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        query_params = self.request.GET
        # print('$GET$', query_params)
        # print('$kwargs$', kwargs)

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
            # print(categories)
            # FIXME not working with pagination and ordering
            queryset = queryset.filter(category__id__in=categories)

        parameters = query_params.copy()
        parameters.pop('page', True)

        ordering = query_params.copy()
        ordering.clear()
        if 'order_by' in parameters:
            ordering['order_by'] = parameters.pop('order_by')[0]

        # print(parameters)
        # print(ordering)

        summary_ym = summary_per_year_month(queryset)

        print('--summary YM-->>', summary_ym)

        summary = summary_per_category(queryset)
        print('--summary C-->>', summary)
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

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     queryset = object_list if object_list is not None else self.object_list
    #     items = list(queryset.all())
        # it1 = items[0]
        #
        # for item in items:
        #     print(' * ',    item, item.name, item.expense_set.all().count())
        # return super().get_context_data(
        #     object_list=queryset,
        #     **kwargs)
