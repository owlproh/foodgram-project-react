from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from users.models import Subscription, User

from .serializers_users import (FollowingSerializer, FollowingShowSerializer,
                                UserSerializer, UserPOSTSerializer)


class UsersViewSet(UserViewSet):
    """Viewset для объектов модели User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserPOSTSerializer
        return UserSerializer

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        url_name='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_me(self, request):
        """"Выдает информацию по своему профилю,
          с возможностью редактирования"""
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_follow(self, request, id):
        """Подписаться/отписаться на/от автора"""
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowingSerializer(
                data={
                    'follower': request.user.id,
                    'author': author.id
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            auth_serializer = FollowingShowSerializer(
                author,
                context={'request': request}
            )
            return Response(
                auth_serializer.data,
                status=status.HTTP_201_CREATED
            )
        follower = get_object_or_404(
            Subscription,
            follower=request.user,
            author=author
        )
        follower.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_follows(self, request):
        """Выдает авторов, на кого подписан пользователь"""
        authors = User.objects.filter(author__follower=request.user)
        paginator = PageNumberPagination()
        result_pages = paginator.paginate_queryset(
            queryset=authors,
            request=request
        )
        serializer = FollowingShowSerializer(
            result_pages,
            context={'request': request},
            many=True
        )
        return paginator.get_paginated_response(serializer.data)
