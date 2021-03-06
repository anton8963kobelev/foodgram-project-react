# Generated by Django 3.2.9 on 2021-12-07 19:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(limit_value=1, message='Время приготовления должно быть больше 0')]),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(limit_value=1, message='Количество ингредиента должно быть больше 0')]),
        ),
    ]
