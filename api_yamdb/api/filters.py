import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(
        field_name='genre__slug', lookup_expr='exact')
    category = django_filters.CharFilter(
        field_name='category__slug', lookup_expr='exact')
    name = django_filters.CharFilter(lookup_expr='icontains')
    year = django_filters.NumberFilter()

    class Meta:
        model = Title
        fields = ['genre', 'category', 'name', 'year']
