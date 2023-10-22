import webcolors
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from django.db import transaction
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User


MAX_LIMIT = 32000
MIN_LIMIT = 1


class UserSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, validated_data):
        if (
            self.context.get('request')
            and not self.context['request'].user.is_anonymous
        ):
            return (
                self.context['request']
                .user.subscriber.filter(author=validated_data)
                .exists()
            )
        return False


class UserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

class PasswordSetSerializer(UserSerializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            "current_password",
            "new_password",
        )

    def validate(self, data):
        user = self.context["request"].user

        if not user.check_password(data["current_password"]):
            raise serializers.ValidationError("Неверный старый пароль.")

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


# class Set_PasswordSerializer(serializers.Serializer):
#
#     current_password = serializers.CharField()
#     new_password = serializers.CharField()
#
#     def validate(self, validated_data):
#         try:
#             validate_password(validated_data['new_password'])
#         except exceptions.ValidationError as exept:
#             raise serializers.ValidationError(
#                 {'new_password': list(exept.messages)}
#             )
#         return super().validate(validated_data)
#
#     def update(self, instance, validated_data):
#         if not instance.check_password(validated_data['current_password']):
#             raise serializers.ValidationError(
#                 {'current_password': 'Неправильный пароль.'}
#             )
#         if (
#             validated_data['current_password']
#             == validated_data['new_password']
#         ):
#             raise serializers.ValidationError(
#                 {'new_password': 'Новый пароль должен отличаться от текущего.'}
#             )
#         instance.set_password(validated_data['new_password'])
#         instance.save()
#         return validated_data


class RecipeListSerializer(serializers.ModelSerializer):

    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

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
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def validate(self, validated_data):
        if self.context['request'].user == validated_data:
            raise serializers.ValidationError(
                {'errors': 'Нет смысла подписаться на себя.'}
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


class Hex2NameColor(serializers.Field):

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializer(serializers.ModelSerializer):

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerialiser(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerialiser(
        many=True, source='recipe_ingredients'
    )
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
            'name',
            'cooking_time',
            'text',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.favorite_user.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.shopping_user.filter(recipe=obj).exists()
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):

    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(
        max_value=MAX_LIMIT, min_value=MIN_LIMIT
    )

    class Meta:
        model = Recipe
        fields = (
            'name',
            'cooking_time',
            'text',
            'tags',
            'ingredients',
            'image',
            'author',
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        list = []
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Нужно выбрать хотя бы один ингредиент!'})
        for ingredient in ingredients:
            amount = ingredient['amount']
            if ingredient['id'] in list:
                raise serializers.ValidationError({
                    'ingredient': 'Ингредиенты не могут повторяться!'
                })
            list.append(ingredient['id'])
            if int(amount) < 1:
                raise serializers.ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0!'
                })
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Нужно выбрать хотя бы один тег!'})
        return data

    def add_ingredients(self, recipe, ingredients):
        objs = []
        for ingredient_data in ingredients:
            objs.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data['amount'],
                )
            )
        return RecipeIngredient.objects.bulk_create(objs)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)
        self.add_ingredients(instance, ingredients)
        return instance

    @transaction.atomic
    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.add_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data
