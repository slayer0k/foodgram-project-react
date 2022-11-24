from rest_framework import mixins, response, status, viewsets


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


class CreateDestroyView(
    mixins.CreateModelMixin, mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    def destroy(self, request, *args, **kwargs):
        model = self.get_serializer_class.Meta.model
        self.perform_destroy(model)
        print(model)
        response.Response(model)

    def perform_destroy(self, instance):
        return response.Response(instance, status=status.HTTP_200_OK)
