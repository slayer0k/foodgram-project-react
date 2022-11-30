from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.mixins import CreateDestroyView, ListRetrieve, LookCreate
from api.pagination import RecipesPagination
from api.permissions import OwnerOrAdmin
from api.response_pdf import get_pdf
from api.serializers import (ChangePassword, FavoritesSerializer,
                             FollowSerializer, IngredientsSerializer,
                             RecipesSerializer, ShoppingCartSerializer,
                             SubscriptionSerializer, TagsSerializer,
                             UserCreateSerializer, UserSerializer)
from foodgram.models import Ingredients, Recipes, Tags

User = get_user_model()


class UserViewSet(LookCreate):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = RecipesPagination

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'POST':
            return UserCreateSerializer
        if self.action == 'subscriptions':
            return SubscriptionSerializer
        return UserSerializer

    def get_instance(self):
        return self.request.user

    @action(
        detail=False, methods=['get'], url_name='me',
        url_path='me', permission_classes=(IsAuthenticated, )
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        detail=False, methods=['POST'],
        url_name='set_password', url_path='set_password',
        permission_classes=(IsAuthenticated, )
    )
    def set_password(self, request):
        serializer = ChangePassword(
            data=request.data, context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'], url_name='subscriptions',
        url_path='subscriptions'
    )
    def subsrciptions(self, request):
        queryset = self.filter_queryset(User.objects.filter(
            subscribers__subscriber=request.user
        ))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(queryset, many=True)
        return Response(serializer.data)


class TagsViewSet(ListRetrieve):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = [OwnerOrAdmin]
    pagination_class = RecipesPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Recipes.objects.all()
        params = self.request.query_params
        if params.get('is_favorited') == '1':
            queryset = queryset.filter(favorited__user=self.request.user)
        if params.get('is_in_shopping_cart') == '1':
            queryset = queryset.filter(
                is_shopping_cart__user=self.request.user
            )
        if params.get('author'):
            queryset = queryset.filter(author=params['author'])
        if params.getlist('tags'):
            queryset = queryset.filter(
                tags__slug__in=params.getlist('tags')).distinct()
        return queryset

    @action(
        detail=False, methods=['get'], url_name='download_shoplist',
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        result = Recipes.objects.filter(
            is_shopping_cart__user=request.user
        ).values(
            'recipe_ingredient__ingredient__name',
            'recipe_ingredient__ingredient__measuring_unit'
        ).order_by(
            'recipe_ingredient__ingredient__name'
        ).annotate(count=Sum('recipe_ingredient__amount'))
        return get_pdf(result)


class IngredientsViewSet(ListRetrieve):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


class ShopingCart(CreateDestroyView):
    serializer_class = ShoppingCartSerializer
    user_field = 'user'
    object_field = 'recipe'
    object_model = Recipes
    fail_message = 'Этого рецепта нету в корзине'


class FavoritesView(CreateDestroyView):
    serializer_class = FavoritesSerializer
    user_field = 'user'
    object_field = 'recipe'
    object_model = Recipes
    fail_message = 'У вас нету этого рецепта в избранном'


class SubscribeView(CreateDestroyView):
    serializer_class = FollowSerializer
    user_field = 'subscriber'
    object_field = 'author'
    object_model = User
    fail_message = 'Такой подписки не существует'
