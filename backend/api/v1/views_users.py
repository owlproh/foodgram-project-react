from api.v1.pagination import CustomPagination
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscription

from .serializers_users import (FollowingSerializer, FollowingShowSerializer,
                                MyUserSerializer)

User = get_user_model()


class UsersViewSet(UserViewSet):
    """Viewset для объектов модели User"""
    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    pagination_class = CustomPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        url_name='me',
        permission_classes=(permissions.IsAuthenticatedOrReadOnly, )
    )
    def get_me(self, request):
        """"Выдает информацию по своему профилю,
          с возможностью редактирования"""
        if request.method == 'PATCH':
            serializer = MyUserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = MyUserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(permissions.IsAuthenticated, )
    )
    def get_follow(self, request, id):
        """Подписаться/отписаться на/от автора"""
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowingSerializer(
                data={
                    'follower': user.id,
                    'author': author.id
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        follower = get_object_or_404(
            Subscription,
            follower=user,
            author=author
        )
        follower.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(permissions.IsAuthenticated, )
    )
    def get_follows(self, request):
        """Выдает авторов, на кого подписан пользователь"""
        user = request.user
        authors = User.objects.filter(author__follower=user)
        result_pages = self.paginate_queryset(authors)
        serializer = FollowingShowSerializer(
            result_pages,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)
