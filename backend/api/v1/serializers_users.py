from django.contrib.auth.hashers import make_password
from djoser.serializers import UserCreateSerializer, UserSerializer
from foodgram.settings import RECIPES_LIMIT
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscription, User

taboo_logins = ('me', 'admin', 'user')


class UserPOSTSerializer(UserCreateSerializer):
    """Сериализатор модели User для POST-запросов"""
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
            'email'
        )

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

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password')
        )
        user = User.objects.create(**validated_data)
        user.save()
        return user


class UserSerializer(UserSerializer):
    """Сериализатор модели User"""
    is_follower = serializers.SerializerMethodField(read_only=True)

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

    def validate(self, data):
        if data.get('username') in taboo_logins:
            raise serializers.ValidationError(
                'Использовать такой логин запрещено'
            )
        return data

    def get_is_follower(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.author.filter(follower=request.user).exists()


class FollowingSerializer(serializers.ModelSerializer):
    """Сериализатор модели Subscriptions"""
    class Meta:
        model = Subscription
        fields = (
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
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowingShowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписчиков"""
    recipes = serializers.SerializerMethodField()
    recipes_cnt = serializers.SerializerMethodField()
    is_follower = serializers.SerializerMethodField(read_only=True)

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

    def get_recipes(self, obj):
        """Получаем рецепты автора"""
        recipes_author = obj.recipes.all()[:RECIPES_LIMIT]
        return FollowingShowRecipeSerializer(
            recipes_author,
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
