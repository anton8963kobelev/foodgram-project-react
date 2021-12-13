import io

import reportlab
from django.http import FileResponse
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from foodgram.settings import BASE_DIR
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follow, User

from .paginations import CustomPaginator
from .permissions import (IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly,
                          IsAuthenticatedReadOnly)
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipeLightSerializer, RecipeSerializer,
                          TagSerializer)
from .utils import get_delete, get_ingredients_unique_list, queryset_filter


class UserCustomViewSet(UserViewSet):
    pagination_class = CustomPaginator
    permission_classes = (IsAuthenticatedReadOnly,)

    def get_permissions(self):
        if (self.action == "list" or self.action == 'retrieve'
                or self.action == 'create'):
            return (permissions.AllowAny(),)
        if self.action == "set_password":
            return (IsAuthorOrAdminOrReadOnly(),)
        if self.action == "destroy":
            return (permissions.IsAdminUser(),)
        return super().get_permissions()

    @action(
        detail=False,
        methods=['get', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path=r'(?P<id>[\d]+)/subscribe'
    )
    def subscribe(self, request, **kwargs):
        return get_delete(
            self,
            request,
            model_1=User,
            model_2=Follow,
            serializer=FollowSerializer,
            message='подписка',
            **kwargs
        )

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        users = queryset_filter(
            self,
            model_id_list=Follow,
            model_main=User,
            value='author_id'
        )
        paginator = CustomPaginator()
        response = paginator.generate_response(
            users,
            FollowSerializer,
            request
        )
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
            queryset = queryset_filter(
                self,
                model_id_list=Favorite,
                model_main=Recipe,
                value='recipe_id'
            )
        if self.request.query_params.get('is_in_shopping_cart'):
            queryset = queryset_filter(
                self,
                model_id_list=ShoppingCart,
                model_main=Recipe,
                value='recipe_id'
            )
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author__id=author_id)
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['get', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path=r'(?P<id>[\d]+)/favorite'
    )
    def recipe_in_favorite(self, request, **kwargs):
        return get_delete(
            self,
            request,
            model_1=Recipe,
            model_2=Favorite,
            serializer=RecipeLightSerializer,
            message='избранное',
            **kwargs
        )

    @action(
        detail=False,
        methods=['get', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path=r'(?P<id>[\d]+)/shopping_cart'
    )
    def recipe_in_shopping_cart(self, request, **kwargs):
        return get_delete(
            self,
            request,
            model_1=Recipe,
            model_2=ShoppingCart,
            serializer=RecipeLightSerializer,
            message='список покупок',
            **kwargs
        )

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        in_shopping_cart = ShoppingCart.objects.filter(
            user_id=request.user.id
        ).values('recipe_id')
        ingredients_unique_list = get_ingredients_unique_list(
            self,
            in_shopping_cart
        )
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        reportlab.rl_config.TTFSearchPath.append(str(BASE_DIR) + '/static')
        pdfmetrics.registerFont(TTFont('FreeSans-LrmZ', 'FreeSans-LrmZ.ttf'))
        p.setFont('FreeSans-LrmZ', 16)
        x = 774
        for ingredient in ingredients_unique_list:
            p.drawString(
                72,
                x,
                f"- {ingredient['name']} - {ingredient['amount']}"
            )
            x -= 18
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_cart.pdf'
        )
