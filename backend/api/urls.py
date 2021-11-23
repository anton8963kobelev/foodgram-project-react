from django.urls import include, path
from rest_framework import routers
# from rest_framework.authtoken import views

from .views import TagViewSet, IngredientViewSet


router = routers.DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
