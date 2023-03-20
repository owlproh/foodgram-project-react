from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all()
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_shopper"
    )
    is_favorited = filters.BooleanFilter(
        method="filter_favors"
    )

    def filter_shopper(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_cart__user=user)
        return queryset

    def filter_favors(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorite__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
        )


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)
