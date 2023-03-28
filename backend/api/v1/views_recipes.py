from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientToRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly
from .serializers_recipes import (CartSerializer, IngredientSerializer,
                                  RecipeGETSerializer, RecipeSerializer,
                                  TagSerializer)
from .serializers_users import FollowingShowRecipeSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    """Viewset для объектов модели Ingredient"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filter_class = IngredientFilter
    search_fields = ('^name', )


class TagViewSet(viewsets.ModelViewSet):
    """Viewset для объектов модели Tag"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset для объектов модели Recipe"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsOwnerOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filter_class = RecipeFilter

    def get_serializer_class(self):
        """Определяет какой сериализатор нужен
         (в зависимости от метода запроса)"""
        if self.request.method in SAFE_METHODS == 'GET':
            return RecipeGETSerializer
        return RecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects.select_related(
           'author'
        ).prefetch_related(
            'ingredients',
            'tags'
        )
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                )
            )
        return queryset

    def perform_create(self, serializer):
        """"Передает в поле author данные о пользователе"""
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        """Удаляет объект класса рецепт"""
        instance.delete()

    @action(
            methods=['POST', 'DELETE'],
            detail=True,
            url_path='favorite',
            url_name='favorite',
            permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Для добавления/удаления в/из Избранное"""
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            Favorite.objects.create(
                user=request.user,
                recipe=recipe
            )
            serializer = FollowingShowRecipeSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if Favorite.objects.filter(user=request.user, recipe__id=pk).exists():
            Favorite.objects.filter(user=request.user, recipe__id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
            methods=['POST', 'DELETE'],
            detail=True,
            url_path='shopping_cart',
            url_name='shopping_cart',
            permission_classes=[permissions.IsAuthenticated]
    )
    def cart(self, request, pk):
        """Для добавления/удаления в/из корзину"""
        user = request.user
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, id=pk)
            instance = ShoppingCart.objects.create(
                user=user,
                recipe=recipe
            )
            serializer = CartSerializer(instance)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if ShoppingCart.objects.filter(
            user=user, recipe__id=pk
        ).exists():
            ShoppingCart.objects.filter(
                user=user,
                recipe__id=pk
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Выгрузка списка покупок в .txt формате"""
        user = request.user
        ingredients = IngredientToRecipe.objects.filter(
            recipe__shopping_cart_r__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = (
            f'Список покупок для пользователя << {user.get_username()} >>\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]}'
            f' - {ingredient["amount"]}'
            f' ({ingredient["ingredient__measurement_unit"]})'
            for ingredient in ingredients
        ])
        shopping_list += '\n\n Приятных покупок!:)'
        filename = "shopping-list.txt"
        response = HttpResponse(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = f"attachment; {filename}"
        return response
