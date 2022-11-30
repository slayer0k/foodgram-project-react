
from django.urls import include, path
from rest_framework import routers

from api.views import (FavoritesView, IngredientsViewSet, RecipesViewSet,
                       ShopingCart, SubscribeView, SubscriptionsViewSet,
                       TagsViewSet, UserViewSet)

router = routers.DefaultRouter()
router.register('users/subscriptions', SubscriptionsViewSet, basename='subs')
router.register('users', UserViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path(
        'recipes/<int:pk>/favorite/', FavoritesView.as_view(),
        name='favorites'
    ),
    path(
        'recipes/<int:pk>/shopping_cart/', ShopingCart.as_view(),
        name='shoplist'
    ),
    path(
        'users/<int:pk>/subscribe/', SubscribeView.as_view(),
        name='subscribe'
    ),
]
