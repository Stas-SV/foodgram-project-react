from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from recipes.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'author',
            'image',
            'pub_date'
        )