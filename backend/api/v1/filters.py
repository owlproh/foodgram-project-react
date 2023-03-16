from django_filters import CharFilter, FilterSet
from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all()
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
        if self.request.query_params.get("is_favorited"):
            qs = qs.filter(recipe__user=self.request.user)
        if self.request.query_params.get("is_in_shopping_cart"):
            qs = qs.filter(recipe__user=self.request.user)
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
    name = CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)
