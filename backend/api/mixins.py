from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.response import Response


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

    representation_class = None
    model = None
    object_model = None
    user_field = None
    fail_message = None
    permission_classes = [permissions.IsAuthenticated, ]

    def user(self):
        return self.request.user

    def get_second_object(self):
        return get_object_or_404(
            self.object_model, pk=self.kwargs.get('pk')
        )

    def get_model(self):
        return self.serializer_class.Meta.model

    def data(self):
        return {
            self.user_field: self.user(),
            self.object_field: self.get_second_object()
        }

    def context(self):
        return {'request': self.request}

    def delete(self, request, pk):
        try:
            object = self.model.objects.get(**self.data())
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except self.model.DoesNotExist:
            return Response(
                self.fail_message, status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request, pk):
        object, created = self.model.objects.get_or_create(**self.data())
        if not created:
            return Response(
                'Такая связь уже существует',
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            self.representation_class(
                self.get_second_object(), context=self.context()
            ).data,
            status=status.HTTP_201_CREATED
        )
