from django.urls import include, path, re_path
from djoser.views import TokenCreateView
from rest_framework import routers

from .views_recipes import IngredientViewSet, RecipeViewSet, TagViewSet
from .views_users import User_ViewSet

router = routers.DefaultRouter()

router.register(r'users', User_ViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    re_path(r'^auth/token/login/?$', TokenCreateView.as_view(), name='login'),
]
