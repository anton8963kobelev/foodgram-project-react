from django.urls import include, path
from rest_framework import routers

from .views import (TagViewSet, IngredientViewSet, UserCustomViewSet,
                    RecipeViewSet)


router = routers.DefaultRouter()
router.register(r'users', UserCustomViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
