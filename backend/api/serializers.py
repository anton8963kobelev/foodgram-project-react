import base64, uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from recipes.models import Tag, Ingredient, Recipe
from djoser.serializers import UserSerializer, UserCreateSerializer

from users.models import User, Follow
from recipes.models import Recipe


class Base64ToImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)
            return data


class UserCreateCustomSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')


class UserCustomSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request', None)
        if not request:
            return True
        user = request.user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    # tags = TagSerializer(many=True)
    # author = UserCustomSerializer(required=False)
    # ingredients = IngredientSerializer(many=True, required=False)  # required - временно
    # is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ToImageField()

    class Meta:
        model = Recipe
        # fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
        #           'is_in_shopping_cart', 'name', 'image', 'text',
        #           'cooking_time')
        fields = ('id', 'name', 'image', 'text', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSerializer(many=True, read_only=True, required=False)  # пока нет RecipeSerializer
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request', None)
        if not request:
            return True
        user = request.user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
