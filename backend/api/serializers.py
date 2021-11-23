from rest_framework import serializers
from recipes.models import Tag, Ingredient
from djoser.serializers import UserSerializer, UserCreateSerializer

from users.models import User, Follow


class UserCreateCustomSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')


class UserCustomSerializer(UserSerializer):
    # is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')
                  # 'is_subscribed')

    # def get_is_subscribed(self, obj):
    #     user = request.user
    #     author = obj.username
    #     return Follow.objects.get(user=user, author=author).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


# class RecipeSerializer(serializers.ModelSerializer):
#     author = AuthorSerializer(read_only=True)
