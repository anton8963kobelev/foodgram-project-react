from django.urls import include, path
from rest_framework import routers

from .views import (TagViewSet, IngredientViewSet, UserCustomViewSet,
                    FollowAPIView)


router = routers.DefaultRouter()
router.register(r'users', UserCustomViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
# router.register(r'users/(?P<user_id>\d+)/subscribe', FollowViewSet,
#                 basename='subscribes')

urlpatterns = [
    path('users/<int:user_id>/subscribe/', FollowAPIView.as_view()),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
