from django.http import FileResponse
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientToRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly
from .serializers_recipes import (CartSerializer, FavoriteSerializer,
                                  IngredientSerializer, RecipeGETSerializer,
                                  RecipeSerializer, TagSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    """Viewset для объектов модели Ingredient"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filtreset_class = IngredientFilter
    search_fields = ('^name',)
    ordering_fields = ('^name',)


class TagViewSet(viewsets.ModelViewSet):
    """Viewset для объектов модели Tag"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset для объектов модели Recipe"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterser_class = RecipeFilter
    ordering = ('-pub_date',)

    def get_queryset(self):
        return (
            super().get_queryset().annotate(
                is_in_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=self.request.user.id,
                        id=OuterRef("pk")
                    )
                ),
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=self.request.user.id,
                        id=OuterRef("pk")
                    )
                ),
            )
        )

    def get_serializer_class(self):
        """Определяет какой сериализатор нужен
         (в зависимости от метода запроса)"""
        if self.request.method == 'GET':
            return RecipeGETSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """"Передает в поле author данные о пользователе"""
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        """Удаляет объект класса рецепт"""
        if self.request.user != instance.author:
            raise Exception('Только автор может удалять рецепт')
        instance.delete()

    @action(
            methods=['POST', 'DELETE'],
            detail=True,
            url_path='favorite',
            url_name='favorite',
            permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """Для добавления/удаления в/из Избранное"""
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            instance = Favorite.objects.create(
                user=request.user,
                recipe=recipe
            )
            serializer = FavoriteSerializer(instance)
            return Response(
                data=serializer.data,
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
            permission_classes=(permissions.IsAuthenticated,)
    )
    def cart(self, request, pk):
        """Для добавления/удаления в/из корзину"""
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            instance = ShoppingCart.objects.create(
                user=request.user,
                recipe=recipe
            )
            serializer = CartSerializer(instance)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        if ShoppingCart.objects.filter(
            user=request.user, recipe__id=pk
        ).exists():
            ShoppingCart.objects.filter(
                user=request.user, recipe__id=pk
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Выгрузка списка покупок в .txt формате"""
        user = request.user
        purchases = ShoppingCart.objects.filter(user=user)
        file = 'shopping-list.txt'
        with open(file, 'w') as f:
            shop_cart = dict()
            for purchase in purchases:
                ingredients = IngredientToRecipe.objects.filter(
                    recipe=purchase.recipe.id
                )
                for r in ingredients:
                    i = Ingredient.objects.get(pk=r.ingredient.id)
                    point_name = f'{i.name} ({i.measurement_unit})'
                    if point_name in shop_cart.keys():
                        shop_cart[point_name] += r.amount
                    else:
                        shop_cart[point_name] = r.amount

            for name, amount in shop_cart.items():
                f.write(f'* {name} - {amount}\n')

        return FileResponse(open(file, 'rb'), as_attachment=True)
