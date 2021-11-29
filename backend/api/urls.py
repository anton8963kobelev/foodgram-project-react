from django.urls import include, path
from rest_framework import routers

from .views import (TagViewSet, IngredientViewSet, UserCustomViewSet,
                    FollowAPIView, RecipeViewSet, FavoriteAPIView,
                    ShoppingCartAPIView)


router = routers.DefaultRouter()
router.register(r'users', UserCustomViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('users/<int:user_id>/subscribe/', FollowAPIView.as_view()),
    path('recipes/<int:recipe_id>/favorite/', FavoriteAPIView.as_view()),
    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppingCartAPIView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
