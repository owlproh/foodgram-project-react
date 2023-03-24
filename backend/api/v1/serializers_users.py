from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscription


User = get_user_model()
taboo_logins = ('me', 'admin', 'user')


class MyUserSerializer(UserSerializer):
    """Сериализатор модели User"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def validate(self, data):
        if data.get('username') in taboo_logins:
            raise serializers.ValidationError(
                'Использовать такой логин запрещено'
            )
        return data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user
        if not request or user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed'
        )


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

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'first_name',
            'last_name',
            'email'
        )
        extra_kwargs = {'password': {'write_only': True}}


class FollowingSerializer(serializers.ModelSerializer):
    """Сериализатор модели Subscriptions"""
    def validate(self, data):
        if not data.get('user'):
            raise KeyError(
                'Не заполнено поле user!'
            )
        if data.get('user') == data.get('author'):
            raise serializers.ValidationError(
                'На себя подписываться не хорошо!'
            )
        return data

    class Meta:
        model = Subscription
        fields = (
            'id',
            'user',
            'author'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого автора'
            )
        ]


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


class FollowingShowSerializer(MyUserSerializer):
    """Сериализатор для подписчиков"""
    recipes = serializers.SerializerMethodField()
    count_recipes = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        """Получаем рецепты автора"""
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        if limit:
            return FollowingShowRecipeSerializer(
                Recipe.objects.filter(author=obj)[:int(limit)],
                context={'request': request},
                many=True
            ).data
        return FollowingShowRecipeSerializer(
            Recipe.objects.filter(author=obj),
            context={'request': request},
            many=True
        ).data

    def get_count_recipes(self, obj):
        """Считаем количество рецептов"""
        return obj.recipes.count()

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
            'count_recipes'
        )
