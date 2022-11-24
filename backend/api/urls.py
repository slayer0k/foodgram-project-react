
from django.urls import include, path
from rest_framework import routers

from api.views import RecipesViewSet, TagsViewSet, UserViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
# router.register('', FavoritesViewSet, basename='favorites')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    # path('fav/', FavoritesViewSet.as_view())
]
