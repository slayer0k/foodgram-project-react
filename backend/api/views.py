from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.mixins import CreateDestroyView, ListRetrieve, LookCreate
from api.serializers import (ChangePassword, CreateRecipeSerializer,
                             FollowSerializer, RecipesSerializer,
                             SubscriptionSerializer, TagsSerializer,
                             UserCreateSerializer, UserSerializer)
from foodgram.models import Favorites, Recipes, Subscriptions, Tags

User = get_user_model()


class UserViewSet(LookCreate):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'POST':
            return UserCreateSerializer
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
        detail=False, methods=['delete', 'post'], url_name='subscribe',
        url_path=r'(?P<pk>\d+)/subscribe',
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        if request.method == 'DELETE':
            Subscriptions.objects.filter(
                author=author, subscriber=request.user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = FollowSerializer(
            data={'author': author, 'subscriber': request.user},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author=author, subscriber=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False, methods=['get'], url_name='subscriptions',
        url_path='subscriptions'
    )
    def subsrciptions(self, request):
        queryset = User.objects.filter(
            subscribers__subscriber=request.user
        )
        serializer = SubscriptionSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)


class TagsViewSet(ListRetrieve):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
