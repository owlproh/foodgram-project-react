from django.urls import include, path
from rest_framework import routers

from .views_recipes import IngredientViewSet, RecipeViewSet, TagViewSet
from .views_users import UsersViewSet

router = routers.DefaultRouter()

router.register(r'users', UsersViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

djoser_urls = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]

urlpatterns = [
    path('', include(router.urls)),
    path('', include(djoser_urls))
]
