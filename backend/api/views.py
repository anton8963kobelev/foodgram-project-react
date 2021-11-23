from rest_framework import viewsets
from djoser.views import UserViewSet

from recipes.models import Tag, Ingredient
from .serializers import TagSerializer, IngredientSerializer


# class UserCustomViewSet(UserViewSet):
#     def get_queryset(self):
#         user = self.request.user
#         queryset = super().get_queryset()
#         if settings.HIDE_USERS and self.action == "list" and not user.is_staff:
#             queryset = queryset.filter(pk=user.pk)
#         return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
