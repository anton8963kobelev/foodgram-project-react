from rest_framework import viewsets
from djoser.views import UserViewSet

from recipes.models import Tag, Ingredient
from users.models import User
from .serializers import TagSerializer, IngredientSerializer, UserCustomSerializer


# class UserCustomViewSet(UserViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserCustomSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
