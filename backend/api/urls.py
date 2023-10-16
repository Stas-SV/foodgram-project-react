from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, TagViewsSet, IngredientViewSet, CustomUserViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewsSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'users', CustomUserViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
