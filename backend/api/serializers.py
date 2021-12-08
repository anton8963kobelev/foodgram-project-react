import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from recipes.models import (Tag, Ingredient, Recipe, RecipeTag,
                            RecipeIngredient, Favorite, ShoppingCart)
from djoser.serializers import UserSerializer, UserCreateSerializer

from users.models import User, Follow


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
        user = request.user
        if not request or not user.is_authenticated:
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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit')
    id = serializers.PrimaryKeyRelatedField(source='ingredient',
                                            queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserCustomSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ToImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_ingredients(self, obj):
        return RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe=obj).all(), many=True
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request', None)
        user = request.user
        if not request or not user.is_authenticated:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request', None)
        user = request.user
        if not request or not user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

    def validate(self, data):
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError('Tags field is required')
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError('Ingredients field is required')
        ingredients = self.initial_data.get('ingredients')
        ingredients_dict = {}
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше нуля')
            if ingredient['id'] not in ingredients_dict:
                instance = ingredient['id']
                ingredients_dict[instance] = True
            else:
                raise serializers.ValidationError(
                    'Ингридиенты не должны повторяться')
            if data['cooking_time'] <= 0:
                raise serializers.ValidationError(
                    'Время готовки должно быть больше нуля')
        return data

    def create(self, validated_data):
        tags = self.initial_data.pop('tags')
        ingredients = self.initial_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag = Tag.objects.get(pk=tag)
            RecipeTag.objects.create(recipe=recipe, tag=current_tag)
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(pk=ingredient['id'])
            amount = ingredient['amount']
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=current_ingredient, amount=amount)
        return recipe

    def update(self, instance, validated_data):
        recipe_id = instance.id
        author_id = instance.author.id
        instance.delete()
        tags = self.initial_data.pop('tags')
        ingredients = self.initial_data.pop('ingredients')
        recipe = Recipe.objects.create(pk=recipe_id, author_id=author_id,
                                       **validated_data)
        for tag in tags:
            current_tag = Tag.objects.get(pk=tag)
            RecipeTag.objects.create(recipe=recipe, tag=current_tag)
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(pk=ingredient['id'])
            amount = ingredient['amount']
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=current_ingredient, amount=amount)
        return recipe


class RecipeLightSerializer(serializers.ModelSerializer):
    image = Base64ToImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        return RecipeLightSerializer(
            Recipe.objects.filter(author=obj).all(), many=True
        ).data

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
