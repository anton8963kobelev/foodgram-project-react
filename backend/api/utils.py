from recipes.models import RecipeIngredient, Ingredient
from collections import Counter
from django.core.exceptions import FieldError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound


def queryset_filter(self, model_id_list, model_main, value):
    instances = model_id_list.objects.filter(
                user_id=self.request.user.id).values(value)
    instance_id_list = []
    for instance in instances:
        instance_id_list.append(instance.get(value))
    return model_main.objects.filter(pk__in=instance_id_list)


def get_ingredients_unique_list(self, in_shopping_cart):
    ingredients_list = []
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
    return ingredients_unique_list


def get_boolean(self, model, obj):
    request = self.context.get('request', None)
    if not request or not request.user.is_authenticated:
        return False
    try:
        return model.objects.filter(user=request.user, author=obj).exists()
    except FieldError:
        return model.objects.filter(user=request.user, recipe=obj).exists()


def get_delete(self, request, **kwargs):
    model_1 = kwargs['model_1']
    model_2 = kwargs['model_2']
    serializer = kwargs['serializer']
    pk = kwargs['id']
    message = kwargs['message']
    instance = viewsets.generics.get_object_or_404(model_1, pk=pk)
    serializer = serializer(instance)
    if request.method == 'GET':
        try:
            if (model_2.objects.filter(user=request.user,
                                       author=instance).exists()):
                return Response(
                    {'error': 'Вы уже подписаны на пользователя'},
                    status=status.HTTP_400_BAD_REQUEST)
            if request.user == instance:
                return Response({'error': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            model_2.objects.create(user=request.user, author=instance)
        except FieldError:
            if (model_2.objects.filter(user=request.user,
                                       recipe=instance).exists()):
                return Response(
                    {'error': f'Рецепт уже добавлен в {message}'},
                    status=status.HTTP_400_BAD_REQUEST)
            model_2.objects.create(user=request.user, recipe=instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        try:
            if not (model_2.objects.filter(user=request.user,
                                           author=instance).exists()):
                return Response(
                    {'error': 'Сначала надо подписаться на пользователя'},
                    status=status.HTTP_400_BAD_REQUEST)
            if request.user == instance:
                return Response({'error': 'Нельзя удалить подпись на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            model_2.objects.filter(user=request.user, author=instance).delete()
        except FieldError:
            if not (model_2.objects.filter(user=request.user,
                                           recipe=instance).exists()):
                return Response(
                    {'error': f'Сначала надо добавить рецепт в {message}'},
                    status=status.HTTP_400_BAD_REQUEST)
            model_2.objects.filter(user=request.user, recipe=instance).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def error404(request):
    raise NotFound(detail="Ошибка 404, страница не найдена", code=404)
