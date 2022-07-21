from rest_framework import mixins, viewsets


class CreateDestroyListModelViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CreateModelViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass
