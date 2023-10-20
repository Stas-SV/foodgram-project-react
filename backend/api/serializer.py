from collections import Counter
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User


class CustomUserSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'is_subscribed')

    def get_is_subscribed(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (
                self.context['request']
                .user.subscriber.filter(author=validated_data)
                .exists()
            )
        return False


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password')

    def validate(self, validated_data):
        data = super().validate(validated_data)
        email = data.get('email')
        username = data.get('username')
        user_full = User.objects.filter(
            email=email, username=username).exists()
        user_email = User.objects.filter(email=email).exists()
        user_username = User.objects.filter(username=username).exists()
        if not user_full and user_email:
            raise serializers.ValidationError('Эта почта занята!')
        if not user_full and user_username:
            raise serializers.ValidationError('Этот username занят!')
        return data


class RecipeListSerializer(serializers.ModelSerializer):

    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

    def get_is_subscribed(self, validated_data):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.subscriber.filter(author=validated_data).exists()
        )

    def get_recipes_count(self, validated_data):
        return validated_data.recipes.count()

    def get_recipes(self, validated_data):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = validated_data.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeListSerializer(recipes, many=True, read_only=True)
        return serializer.data


class SubscribeListSerializer(serializers.ModelSerializer):

    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeListSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

    def validate(self, validated_data):
        if self.context['request'].user == validated_data:
            raise serializers.ValidationError(
                {'errors': 'Подписка невозможна'}
            )
        return validated_data

    def get_is_subscribed(self, validated_data):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.subscriber.filter(author=validated_data).exists()
        )

    def get_recipes_count(self, validated_data):
        return validated_data.recipes.count()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id',
                  'name',
                  'color',
                  'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount')


class RecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'image',
                  'name',
                  'cooking_time',
                  'text')

    def get_is_favorited(self, validated_data):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.favorite_user.filter(recipe=validated_data).exists()
        )

    def get_is_in_shopping_cart(self, validated_data):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.shopping_user.filter(recipe=validated_data).exists()
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id',
                  'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    author = CustomUserSerializer(many=False, read_only=True)
    image = Base64ImageField(max_length=10485760)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients',
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'author',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def create_recipe_ingredients(self, recipe, ingredients):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        ]
        with transaction.atomic():
            RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def validate(self, data):
        image = data.pop('image')
        data.pop('tags')
        tags = self.initial_data.get('tags')
        validated_data = super().validate(data)
        ingredients = self.initial_data.get('ingredients')
        ingredient_ids = [ingredient.get('id') for ingredient in ingredients]
        duplicate_ingredients = [
            ingredient for ingredient,
            count in Counter(ingredient_ids).items() if count > 1]
        if duplicate_ingredients:
            raise serializers.ValidationError(
                f'Найдены дубликаты для идентификаторов ингредиентов:'
                f' {duplicate_ingredients}'
            )
        validated_data['ingredients'] = ingredients
        validated_data['image'] = image
        validated_data['tags'] = tags
        return validated_data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_recipe_ingredients(recipe=recipe, ingredients=ingredients)
        tag_ids = [tag for tag in tags_data]
        tags = Tag.objects.filter(id__in=tag_ids)
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        tags = instance.tags.all()
        tag_serializer = TagSerializer(tags, many=True)
        representation['tags'] = tag_serializer.data
        return representation

    def update(self, recipe, validated_data):
        recipe.ingredients.clear()
        recipe.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.create_recipe_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)


class ChangePasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'current_password',
            'new_password',
        )

    def validate(self, data):
        user = self.context['request'].user

        if not user.check_password(data['current_password']):
            raise serializers.ValidationError('Неверный старый пароль.')

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
