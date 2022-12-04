from django.contrib.auth import get_user_model
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, response, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from api.filters import RecipesFilterSet
from api.mixins import CreateDestroyView, ListRetrieve, ListView
from api.pagination import RecipesPagination
from api.permissions import OwnerOnly
from api.serializers import (IngredientsSerializer, RecipesForSubscribers,
                             RecipesSerializer, SubscriptionSerializer,
                             TagsSerializer, UserSerializer)
from api.utils import get_pdf
from foodgram.models import (Favorites, Ingredients, Recipes, ShopLists,
                             Subscriptions, Tags)

User = get_user_model()


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = RecipesPagination


class TagsViewSet(ListRetrieve):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = [OwnerOnly]
    pagination_class = RecipesPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipesFilterSet

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False, methods=['get'], url_name='download_shoplist',
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        results = request.user.shoplist.all().values(
            'recipe__recipe_ingredient__ingredient__id',
            'recipe__recipe_ingredient__ingredient__name',
            'recipe__recipe_ingredient__ingredient__measuring_unit'
        ).order_by(
            'recipe__recipe_ingredient__ingredient__name'
        ).annotate(count=Sum('recipe__recipe_ingredient__amount'))
        return get_pdf(results)


class IngredientsViewSet(ListRetrieve):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


class ShopingCart(CreateDestroyView):
    representation_class = RecipesForSubscribers
    user_field = 'user'
    object_field = 'recipe'
    object_model = Recipes
    fail_message = 'Этого рецепта нету в корзине'
    model = ShopLists


class FavoritesView(CreateDestroyView):
    representation_class = RecipesForSubscribers
    user_field = 'user'
    object_field = 'recipe'
    object_model = Recipes
    fail_message = 'У вас нету этого рецепта в избранном'
    model = Favorites


class SubscribeView(CreateDestroyView):
    representation_class = SubscriptionSerializer
    model = Subscriptions
    user_field = 'subscriber'
    object_field = 'author'
    object_model = User
    fail_message = 'Такой подписки не существует'

    def post(self, request, pk):
        if self.user() == self.get_second_object():
            return response.Response(
                'Вы не можете подписаться на самого себя',
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().post(request)


class SubscriptionsViewSet(ListView):
    serializer_class = SubscriptionSerializer
    pagination_class = RecipesPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            subscribers__subscriber=self.request.user
        )
