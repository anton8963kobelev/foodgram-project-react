from rest_framework import views, viewsets, permissions, status
from djoser.views import UserViewSet
from djoser.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import action

from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from users.models import User, Follow
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer, FollowSerializer,
                          RecipeLightSerializer)


class UserCustomViewSet(UserViewSet):

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == "list":
            self.permission_classes = settings.PERMISSIONS.user_list
        elif self.action == "set_password":
            self.permission_classes = settings.PERMISSIONS.set_password
        elif self.action == "destroy":
            self.permission_classes = settings.PERMISSIONS.user_delete
        return super().get_permissions()

    @action(detail=False)
    def subscriptions(self, request):
        followings = Follow.objects.filter(
            user_id=request.user.id).values('author_id')
        author_id_list = []
        for follow in followings:
            author_id_list.append(follow.get('author_id'))
        users = User.objects.filter(pk__in=author_id_list)
        serializer = FollowSerializer(users, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAdminUser,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAdminUser,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FollowAPIView(views.APIView):

    def get(self, request, user_id):
        author = viewsets.generics.get_object_or_404(User, pk=user_id)
        serializer = FollowSerializer(author)
        if (Follow.objects.filter(user=request.user,
                                  author=author).exists()):
            return Response(
                {'error': 'Вы уже подписаны на данного пользователя'},
                status=status.HTTP_400_BAD_REQUEST)
        if request.user == author:
            return Response({'error': 'Нельзя подписаться на самого себя'},
                            status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = viewsets.generics.get_object_or_404(User, pk=user_id)
        if request.user == author:
            return Response({'error': 'Нельзя удалить подпись на самого себя'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not (Follow.objects.filter(user=request.user,
                                      author=author).exists()):
            return Response(
                {'error': 'Сначала надо подписаться на данного пользователя'},
                status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.filter(user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteAPIView(views.APIView):

    def get(self, request, recipe_id):
        recipe = viewsets.generics.get_object_or_404(Recipe, pk=recipe_id)
        serializer = RecipeLightSerializer(recipe)
        if (Favorite.objects.filter(user=request.user,
                                    recipe=recipe).exists()):
            return Response(
                {'error': 'Рецепт уже добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = viewsets.generics.get_object_or_404(Recipe, pk=recipe_id)
        if not (Favorite.objects.filter(user=request.user,
                                        recipe=recipe).exists()):
            return Response(
                {'error': 'Сначала надо добавить рецепт в избранное'},
                status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartAPIView(views.APIView):

    def get(self, request, recipe_id):
        recipe = viewsets.generics.get_object_or_404(Recipe, pk=recipe_id)
        serializer = RecipeLightSerializer(recipe)
        if (ShoppingCart.objects.filter(user=request.user,
                                        recipe=recipe).exists()):
            return Response(
                {'error': 'Рецепт уже добавлен в список покупок'},
                status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = viewsets.generics.get_object_or_404(Recipe, pk=recipe_id)
        if not (ShoppingCart.objects.filter(user=request.user,
                                            recipe=recipe).exists()):
            return Response(
                {'error': 'Сначала надо добавить рецепт в список покупок'},
                status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
