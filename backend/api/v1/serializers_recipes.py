import base64

import webcolors
from django.core.files.base import ContentFile
from recipes.models import (Favorite, Ingredient, Ingredient_to_Recipe, Recipe,
                            Shopping_Cart, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .serializers_users import UserSerializer


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError(
                'Для этого цвета не придумали названия'
            )
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag"""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient"""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class ItRSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient_to_Recipe."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = Ingredient_to_Recipe
        fields = ('id', 'cnt')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели Favorite"""
    class Meta:
        model = Favorite
        fields = (
            'recipe',
            'user',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже добавлен в Избранное'
            )
        ]


class FULLItRSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient_to_Recipe"""
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = Ingredient_to_Recipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'cnt'
        )


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор модели Shopping_Cart"""
    class Meta:
        model = Shopping_Cart
        fields = (
            'recipe',
            'user',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Shopping_Cart.objects.all(),
                fields=("recipe", "user"),
                message='Этот рецепт уже в корзине'
            )
        ]


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe для GET-запросов"""
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_cart = serializers.SerializerMethodField(read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(required=True, allow_null=True)
    tags = TagSerializer(many=True, read_only=True)

    @staticmethod
    def get_ingredients(obj):
        ingredients = Ingredient_to_Recipe.objects.filter(recipe=obj)
        return FULLItRSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favorite.filter(recipe=obj).exists()

    def get_is_in_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_cart.filter(recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_cart',
            'author',
            'pub_date'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe"""
    ingredients = ItRSerializer(many=True)
    image = Base64ImageField(required=True, allow_null=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
            'pub_date'
        )

    def validate_ingredients(self, data):
        ingredients = data['ingredients']
        unique_ings = []
        for ingredient in ingredients:
            name = ingredient['id_ingredient']
            if int(ingredient['cnt']) < 1:
                raise serializers.ValidationError(
                    f'Не корректное количество для {name}'
                )
            if name not in unique_ings:
                unique_ings.append(name)
            else:
                raise serializers.ValidationError('Ингредиенты повторяются!')
        return data

    @staticmethod
    def create_ingredients(self, ingredients, recipe):
        Ingredient_to_Recipe.objects.bulk_create(
            [Ingredient_to_Recipe(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                cnt=ingredient.get('cnt')
            ) for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        Ingredient_to_Recipe.objects.filter(recipe=instance).all().delete()
        self.create_ingredients(validated_data.get('ingredients'), instance)
        instance.save()
        return instance

    def to_representation(self, recipe):
        return RecipeGETSerializer(recipe).data
