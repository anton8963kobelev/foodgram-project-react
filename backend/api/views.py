from rest_framework import viewsets
from rest_framework.decorators import action
from djoser.views import UserViewSet
from djoser.conf import settings

from recipes.models import Tag, Ingredient
from .serializers import TagSerializer, IngredientSerializer


class UserCustomViewSet(UserViewSet):

    def get_permissions(self):
        if self.action == "create" or self.action == "list":
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == "set_password":
            self.permission_classes = settings.PERMISSIONS.set_password
        return super().get_permissions()

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
