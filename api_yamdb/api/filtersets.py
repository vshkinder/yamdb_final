from django_filters import CharFilter, FilterSet, NumberFilter
from reviews.models import Title


class TitleFilter(FilterSet):
    category = CharFilter(field_name="category__slug", lookup_expr="exact")
    genre = CharFilter(field_name="genre__slug", lookup_expr="exact")
    name = CharFilter(field_name="name", lookup_expr="contains")
    year = NumberFilter(field_name="year", lookup_expr="exact")

    class Meta:
        model = Title
        fields = ("category", "genre", "name", "year")
