from rest_framework import views, viewsets, permissions, mixins, serializers, status
from djoser.views import UserViewSet
from djoser.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import action

from recipes.models import Tag, Ingredient
from users.models import User, Follow
from .permissions import IsAuthenticatedReadOnly
from .serializers import (TagSerializer, IngredientSerializer,
                          UserCustomSerializer, FollowSerializer)


class UserCustomViewSet(UserViewSet):

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == "list":
            self.permission_classes = settings.PERMISSIONS.user_list
        elif self.action == "set_password":
            self.permission_classes = settings.PERMISSIONS.set_password
        elif self.action == "destroy":
            self.permission_classes = settings.PERMISSIONS.user_delete
        return super().get_permissions()

    @action(detail=False)
    def subscriptions(self, request):
        followings = Follow.objects.filter(
            user_id=request.user.id).values('author_id')
        author_id_list = []
        for follow in followings:
            author_id_list.append(follow.get('author_id'))
        users = User.objects.filter(pk__in=author_id_list)
        serializer = FollowSerializer(users, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAdminUser,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAdminUser,)


# class CreateDestroyViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
#                            viewsets.GenericViewSet):
#     pass


class FollowAPIView(views.APIView):
    # serializer_class = UserCustomSerializer
    # permission_classes = (IsAuthenticatedReadOnly,)

    def get(self, request, user_id):
        author = viewsets.generics.get_object_or_404(User, pk=user_id)
        serializer = FollowSerializer(author)
        if (Follow.objects.filter(user=request.user,
                                  author=author).exists()):
            return Response(
                {'error': 'Вы уже подписаны на данного пользователя'},
                status=status.HTTP_400_BAD_REQUEST)
        if request.user == author:
            return Response({'error': 'Нельзя подписаться на самого себя'},
                            status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = viewsets.generics.get_object_or_404(User, pk=user_id)
        if request.user == author:
            return Response({'error': 'Нельзя удалить подпись на самого себя'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not (Follow.objects.filter(user=request.user,
                                      author=author).exists()):
            return Response(
                {'error': 'Сначала надо подписаться на данного пользователя'},
                status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.filter(user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
