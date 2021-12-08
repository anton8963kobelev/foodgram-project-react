from rest_framework import viewsets, permissions, status
from djoser.views import UserViewSet
from djoser.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound

import io
import reportlab
from foodgram.settings import BASE_DIR
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from collections import Counter

from .permissions import IsAuthorOrAdminOrReadOnly, IsAdminOrReadOnly
from .paginations import CustomPaginator
from recipes.models import (Tag, Ingredient, Recipe, Favorite, ShoppingCart,
                            RecipeIngredient)
from users.models import User, Follow
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer, FollowSerializer,
                          RecipeLightSerializer)


def error404(request):
    raise NotFound(detail="Ошибка 404, страница не найдена", code=404)


def queryset_filter(self, model_id_list, model_main, value):
    instances = model_id_list.objects.filter(
                user_id=self.request.user.id).values(value)
    instance_id_list = []
    for instance in instances:
        instance_id_list.append(instance.get(value))
    return model_main.objects.filter(pk__in=instance_id_list)


class UserCustomViewSet(UserViewSet):
    pagination_class = CustomPaginator

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == "list" or self.action == 'retrieve':
            self.permission_classes = settings.PERMISSIONS.user_list
        elif self.action == "set_password":
            self.permission_classes = settings.PERMISSIONS.set_password
        elif self.action == "destroy":
            self.permission_classes = settings.PERMISSIONS.user_delete
        return super().get_permissions()

    @action(detail=False, methods=['get', 'delete'],
            permission_classes=(permissions.IsAuthenticated,),
            url_path=r'(?P<id>[\d]+)/subscribe')
    def subscribe(self, request, **kwargs):
        if request.method == 'GET':
            author = viewsets.generics.get_object_or_404(User, pk=kwargs['id'])
            serializer = FollowSerializer(author)
            if (Follow.objects.filter(user=request.user,
                                      author=author).exists()):
                return Response(
                    {'error': 'Вы уже подписаны на пользователя'},
                    status=status.HTTP_400_BAD_REQUEST)
            if request.user == author:
                return Response({'error': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            author = viewsets.generics.get_object_or_404(User, pk=kwargs['id'])
            if request.user == author:
                return Response({'error': 'Нельзя удалить подпись на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            if not (Follow.objects.filter(user=request.user,
                                          author=author).exists()):
                return Response(
                    {'error': 'Сначала надо подписаться на пользователя'},
                    status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.filter(user=request.user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,),)
    def subscriptions(self, request):
        users = queryset_filter(self, model_id_list=Follow,
                                model_main=User, value='author_id')
        paginator = CustomPaginator()
        response = paginator.generate_response(users, FollowSerializer,
                                               request)
        return response


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('@name',)

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__startswith=name.lower())
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = CustomPaginator

    def get_queryset(self):
        queryset = Recipe.objects.all()
        if self.request.query_params.get('is_favorited'):
            queryset = queryset_filter(self, model_id_list=Favorite,
                                       model_main=Recipe, value='recipe_id')
        if self.request.query_params.get('is_in_shopping_cart'):
            queryset = queryset_filter(self, model_id_list=ShoppingCart,
                                       model_main=Recipe, value='recipe_id')
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author__id=author_id)
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        else:
            queryset = []
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get', 'delete'],
            permission_classes=(permissions.IsAuthenticated,),
            url_path=r'(?P<id>[\d]+)/favorite')
    def recipe_in_favorite(self, request, **kwargs):
        if request.method == 'GET':
            recipe = viewsets.generics.get_object_or_404(Recipe,
                                                         pk=kwargs['id'])
            serializer = RecipeLightSerializer(recipe)
            if (Favorite.objects.filter(user=request.user,
                                        recipe=recipe).exists()):
                return Response(
                    {'error': 'Рецепт уже добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recipe = viewsets.generics.get_object_or_404(Recipe,
                                                         pk=kwargs['id'])
            if not (Favorite.objects.filter(user=request.user,
                                            recipe=recipe).exists()):
                return Response(
                    {'error': 'Сначала надо добавить рецепт в избранное'},
                    status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get', 'delete'],
            permission_classes=(permissions.IsAuthenticated,),
            url_path=r'(?P<id>[\d]+)/shopping_cart')
    def recipe_in_shopping_cart(self, request, **kwargs):
        if request.method == 'GET':
            recipe = viewsets.generics.get_object_or_404(Recipe,
                                                         pk=kwargs['id'])
            serializer = RecipeLightSerializer(recipe)
            if (ShoppingCart.objects.filter(user=request.user,
                                            recipe=recipe).exists()):
                return Response(
                    {'error': 'Рецепт уже добавлен в список покупок'},
                    status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recipe = viewsets.generics.get_object_or_404(Recipe,
                                                         pk=kwargs['id'])
            if not (ShoppingCart.objects.filter(user=request.user,
                                                recipe=recipe).exists()):
                return Response(
                    {'error': 'Сначала надо добавить рецепт в список покупок'},
                    status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.filter(user=request.user,
                                        recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients_list = []
        in_shopping_cart = ShoppingCart.objects.filter(
            user_id=request.user.id).values('recipe_id')
        for recipe in in_shopping_cart:
            recipe_id = recipe.get('recipe_id')
            ingredients = RecipeIngredient.objects.filter(
                recipe_id=recipe_id).values('ingredient_id', 'amount')
            for ingredient in ingredients:
                ingredient_id = ingredient.get('ingredient_id')
                name = Ingredient.objects.get(pk=ingredient_id).name
                measurement_unit = (Ingredient.objects.get(
                                    pk=ingredient_id).measurement_unit)
                amount = ingredient.get('amount')
                ingredient_dict = {
                    'name': f'{name} ({measurement_unit})',
                    'amount': amount,
                }
                ingredients_list.append(ingredient_dict)

        counter = Counter()
        for ingredient in ingredients_list:
            key, value = ingredient.get('name'), ingredient.get('amount')
            counter.update({key: value})

        ingredients_unique_list = [
            {'name': key, 'amount': value} for key, value in counter.items()
        ]

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        reportlab.rl_config.TTFSearchPath.append(str(BASE_DIR) + '/static')
        pdfmetrics.registerFont(TTFont('FreeSans-LrmZ', 'FreeSans-LrmZ.ttf'))
        p.setFont('FreeSans-LrmZ', 16)
        x = 774
        for ingredient in ingredients_unique_list:
            p.drawString(72, x,
                         f"- {ingredient['name']} - {ingredient['amount']}")
            x -= 18
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True,
                            filename='shopping_cart.pdf')
