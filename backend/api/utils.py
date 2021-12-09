from recipes.models import RecipeIngredient, Ingredient
from collections import Counter
from django.core.exceptions import FieldError


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
