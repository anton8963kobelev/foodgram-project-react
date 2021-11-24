from django.urls import include, path
from rest_framework import routers
# from rest_framework.authtoken import views

from .views import TagViewSet, IngredientViewSet, UserCustomViewSet


router = routers.DefaultRouter()
router.register(r'users', UserCustomViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
