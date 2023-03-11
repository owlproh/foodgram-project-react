from django.contrib import admin
from foodgram.settings import LIST_PER_PAGE

from .models import (Favorite, Ingredient, IngredientToRecipe, Recipe,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )
    empty_value_display = '<--пусто-->'
    list_filter = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    list_per_page = LIST_PER_PAGE
    ordering = ('pk',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    empty_value_display = '<--пусто-->'
    list_filter = ('name', 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)
    list_per_page = LIST_PER_PAGE


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'text',
        'cooking_time',
        'author',
        'pub_date',
        'cnt_favorite',

    )
    empty_value_display = '<--пусто-->'
    list_filter = (
        'name',
        'author',
        'pub_date',
    )
    search_fields = (
        'name',
        'author',
        'pub_date',
    )
    ordering = ('-pub_date',)
    list_per_page = LIST_PER_PAGE

    @admin.display(description='В избранном')
    def cnt_favorite(self, obj):
        return obj.favorite.count()


@admin.register(IngredientToRecipe)
class IngRecAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'ingredient',
        'recipe',
        'amount'
    )
    empty_value_display = '<--пусто-->'
    list_filter = (
        'ingredient',
        'recipe',
        'amount'
    )
    search_fields = (
        'ingredient',
        'recipe',
    )
    list_per_page = LIST_PER_PAGE


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe'
    )
    empty_value_display = '<--пусто-->'
    list_filter = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)
    list_per_page = LIST_PER_PAGE


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe'
    )
    empty_value_display = '<--пусто-->'
    list_filter = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)
    list_per_page = LIST_PER_PAGE
