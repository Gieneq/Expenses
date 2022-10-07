from django.views.generic.list import ListView

from .forms import ExpenseSearchForm
from .models import Expense, Category
from .reports import summary_per_category


class ExpenseListView(ListView):
    model = Expense
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        query_params = self.request.GET
        print('$GET$', query_params)
        print('$kwargs$', kwargs)
        queryset = object_list if object_list is not None else self.object_list

        form = ExpenseSearchForm(query_params)
        if form.is_valid():
            cdata = form.cleaned_data
            print('-->', cdata)

            # Ordering
            name = cdata.get('name', '').strip()
            if name:
                queryset = queryset.filter(name__icontains=name)

            from_date, to_date = cdata.get('from_date'), cdata.get('to_date')
            if from_date:
                queryset = queryset.filter(date__gte=from_date)

            if to_date:
                queryset = queryset.filter(date__lt=to_date)

            categories = cdata.get('categories')
            # FIXME not working with pagination and ordering
            # queryset = queryset.filter(category__id__in=categories)

        # Ordering after any forms inputs
        order_by = query_params.get('order_by', '')
        print(order_by)

        if order_by:
            DIR_CHARS = 4
            field_name = order_by[:-DIR_CHARS]
            direction = '' if order_by[-DIR_CHARS+1:].lower() == 'asc' else '-'
            # print(field_name, direction)
            queryset = queryset.order_by(f"{direction}{field_name}")


        # context = {'quer': self.request.GET}
        # print(form)

        return super().get_context_data(
            # context=context,
            form=form,
            object_list=queryset,
            summary_per_category=summary_per_category(queryset),
            **kwargs)


class CategoryListView(ListView):
    model = Category
    paginate_by = 5
