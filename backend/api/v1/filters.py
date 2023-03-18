from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


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
        field_name="is_in_shopping_cart",
        method="filter"
    )
    is_favorited = filters.BooleanFilter(
        field_name="is_favorited",
        method="filter"
    )

    def filter(self, qs, name, value):
        user = self.request.user
        if not user.is_anonymous:
            if self.request.query_params.get("is_favorited"):
                qs = qs.filter(recipe__user=user)
            if self.request.query_params.get("is_in_shopping_cart"):
                qs = qs.filter(recipe__user=user)
        return qs

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
        )


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ["name"]
