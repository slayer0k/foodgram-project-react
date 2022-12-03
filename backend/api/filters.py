import django_filters
from django_filters import FilterSet

from foodgram.models import Recipes, Tags


class RecipesFilterSet(FilterSet):
    author = django_filters.CharFilter(
        field_name='author__id'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug', queryset=Tags.objects.all(),
        to_field_name='slug'
    )

    class Meta:
        model = Recipes
        fields = ('author', 'tags')

    @property
    def qs(self):
        qs = super().qs
        user = self.request.user
        params = self.request.query_params
        if params.get('is_favorited') == '1':
            qs = qs.filter(id__in=user.favorites.all().values('recipe'))
        if params.get('is_in_shopping_cart') == '1':
            qs = qs.filter(id__in=user.shoplist.all().values('recipe'))
        return qs
