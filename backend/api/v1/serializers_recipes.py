import base64

import webcolors
from django.core.files.base import ContentFile
from django.db import transaction
from recipes.models import (Favorite, Ingredient, IngredientToRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .serializers_users import MyUserSerializer


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
    color = Hex2NameColor

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient"""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class ItRSerializer(serializers.ModelSerializer):
    """Сериализатор для модели IngredientToRecipe."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientToRecipe
        fields = ('id', 'amount')


class FULLItRSerializer(serializers.ModelSerializer):
    """Сериализатор модели IngredientToRecipe"""
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientToRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe для GET-запросов"""
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    author = MyUserSerializer(read_only=True)
    ingredients = FULLItRSerializer(
        many=True,
        source='recipe'
    )
    image = Base64ImageField()
    tags = TagSerializer(many=True)

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
            'is_in_shopping_cart',
            'author',
            'pub_date'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe"""
    ingredients = ItRSerializer(many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = MyUserSerializer(read_only=True)

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        unique_ings = []
        for ingredient in ingredients:
            name = ingredient.get('id')
            amount = ingredient.get('amount')
            if type(amount) is str:
                if not amount.isdigit():
                    raise serializers.ValidationError(
                        'Колличество ингредиента должно быть числом!'
                    )
            if int(amount) < 1:
                raise serializers.ValidationError(
                    f'Не корректное количество для {name}'
                )
            if name in unique_ings:
                raise serializers.ValidationError(
                    'Ингредиенты повторяются!'
                )
            unique_ings.append(name)
        return data

    def _create_ingredients(self, ingredients, recipe):
        IngredientToRecipe.objects.bulk_create(
            [IngredientToRecipe(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        try:
            tags_data = validated_data.pop('tags')
            ingredients_data = validated_data.pop('ingredients')
        except Exception:
            raise KeyError(
                'Не предоставлены необходимые данные:'
                'проверьте поля tags и ingredients)'
            )
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self._create_ingredients(ingredients_data, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        try:
            instance.image = validated_data.get('image', instance.image)
            instance.name = validated_data.get('name', instance.name)
            instance.text = validated_data.get('text', instance.text)
            instance.cooking_time = validated_data.get(
                'cooking_time', instance.cooking_time
            )
            instance.tags.clear()
            instance.ingredients.clear()
            tags_data = self.validated_data.get('tags')
            instance.tags.set(tags_data)
            IngredientToRecipe.objects.filter(recipe=instance).all().delete()
            self._create_ingredients(
                validated_data.get('ingredients'),
                instance
            )
            instance.save()
            return instance
        except Exception:
            raise KeyError(
                'Не предоставлены необходимые данные',
                'проверьте все поля формы'
            )

    def to_representation(self, obj):
        return RecipeGETSerializer(obj, context=self.context).data

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


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели Favorite"""

    class Meta:
        model = Favorite
        fields = (
            'id',
            'recipe',
            'user'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
                message='Этот рецепт уже добавлен в Избранное'
            )
        ]


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор модели ShoppingCart"""

    class Meta:
        model = ShoppingCart
        fields = (
            'recipe',
            'user'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=["recipe", "user"],
                message='Этот рецепт уже в корзине'
            )
        ]
