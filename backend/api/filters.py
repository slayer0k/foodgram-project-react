import django_filters

from foodgram.models import Recipes


class RecipesFilterSet(django_filters.FilterSet):

    class Meta:
        model = Recipes
        fields = {
            'tags__slug': {'exact'}
        }
