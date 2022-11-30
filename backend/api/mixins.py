from django.shortcuts import get_object_or_404
from rest_framework import (mixins, permissions, response, status, views,
                            viewsets)


class LookCreate(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    pass


class ListRetrieve(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass


class ListView(
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    pass


class CreateDestroyView(views.APIView):
    '''
    Вьюха для создания и удаления простых связей между объектом
    и авторизованным пользователем
    '''

    serializer_class = None
    object_model = None
    user_field = None
    object_field = None
    fail_message = None
    permission_classes = [permissions.IsAuthenticated, ]

    def get_user(self):
        return self.request.user

    def get_second_object(self):
        return get_object_or_404(
            self.object_model, pk=self.kwargs.get('pk')
        )

    def get_model(self):
        return self.serializer_class.Meta.model

    def data(self):
        return {
            self.user_field: self.get_user(),
            self.object_field: self.get_second_object()
        }

    def context(self):
        return {'request': self.request}

    def get_object(self):
        try:
            object = self.get_model().objects.get(**self.data())
            return object
        except self.get_model().DoesNotExist:
            return None

    def delete(self, request, pk):
        if self.get_object():
            self.get_object().delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(
            self.fail_message, status=status.HTTP_400_BAD_REQUEST
        )

    def post(self, request, pk):
        serializer = self.serializer_class(
            data=self.data(), context=self.context()
        )
        serializer.is_valid()
        serializer.save(**self.data())
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED
        )
