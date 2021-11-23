from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True, default='#000000')
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, related_name='recipe_tags',
                                  through='RecipeTag')
    author = models.ForeignKey(User, related_name='authors',
                               on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient,
                                         related_name='recipe_ingredients',
                                         through='RecipeIngredient')
    name = models.CharField(max_length=200)
    image = models.FileField(upload_to='recipes/%Y-%m-%d/')
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)])
    publication_date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-publication_date',)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(default=1)


class Favorite(models.Model):
    user = (models.ForeignKey(User, on_delete=models.CASCADE,
            related_name='favorite'))
    recipe = (models.ForeignKey(Recipe, on_delete=models.CASCADE,
              related_name='in_favorite'))

    class Meta:
        models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_recipe'
        )


class ShoppingCart(models.Model):
    user = (models.ForeignKey(User, on_delete=models.CASCADE,
            related_name='shopping_cart'))
    recipe = (models.ForeignKey(Recipe, on_delete=models.CASCADE,
              related_name='in_shopping_cart'))

    class Meta:
        models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_recipe'
        )
