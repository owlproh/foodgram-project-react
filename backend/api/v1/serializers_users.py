from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from foodgram.settings import RECIPES_LIMIT
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscription

taboo_logins = ('me', 'admin', 'user')


class UserPOSTSerializer(UserCreateSerializer):
    """Сериализатор модели User для POST-запросов"""

    def validate(self, data):
        if data.get('username') in taboo_logins:
            raise serializers.ValidationError(
                'Использовать такой логин запрещено'
            )
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError(
                'Пользователь с таким логином уже существует'
            )
        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return data

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'first_name',
            'last_name',
            'email'
        )


class UserSerializer(UserSerializer):
    """Сериализатор модели User"""
    is_follower = serializers.SerializerMethodField(read_only=True)

    def validate(self, data):
        if data.get('username') in taboo_logins:
            raise serializers.ValidationError(
                'Использовать такой логин запрещено'
            )
        return data

    def get_is_follower(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.author.filter(follower=user).exists()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_follower'
        )


class FollowingSerializer(serializers.ModelSerializer):
    """Сериализатор модели Subscriptions"""
    class Meta:
        model = Subscription
        fields = (
            'id',
            'follower',
            'author'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('follower', 'author'),
                message='Вы уже подписаны на этого автора'
            )
        ]

    def validate(self, data):
        if not data.get('follower'):
            raise KeyError(
                'Не заполнено поле follower!'
            )
        if data.get('follower') == data.get('author'):
            raise serializers.ValidationError(
                'Не пытайтесь накрутить подписчиков!'
            )
        return data


class FollowingShowRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов автора у подписчика"""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = fields


class FollowingShowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписчиков"""
    recipes = serializers.SerializerMethodField()
    recipes_cnt = serializers.SerializerMethodField()
    is_follower = serializers.SerializerMethodField(read_only=True)

    def get_recipes(self, obj):
        """Получаем рецепты автора"""
        request = self.context.get('request')
        return FollowingShowRecipeSerializer(
            Recipe.objects.filter(author=obj)[:RECIPES_LIMIT],
            context={'request': request},
            many=True
        ).data

    def get_recipes_cnt(self, obj):
        """Считаем количество рецептов"""
        return obj.recipes.count()

    def get_is_follower(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.author.filter(follower=request.user).exists()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_follower',
            'recipes',
            'recipes_cnt'
        )
