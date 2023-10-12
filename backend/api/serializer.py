from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from recipes.models import Recipe, Tag, Ingredient, Favorite, ShoppingList
from users.models import User
from djoser.serializers import UserCreateSerializer, UserSerializer


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = '__all__'


class CustomUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class ShoppingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = '__all__'
