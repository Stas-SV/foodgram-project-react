from django.core import validators
from django.core.validators import MinValueValidator
from django.db import models
from colorfield.fields import ColorField
from users.models import User

MAX_LENGTH = 200
MAX_STRING = 150
MAX_LIMIT = 32000
MIN_LIMIT = 1


class Tag(models.Model):
    name = models.CharField(verbose_name='Название',
                            max_length=MAX_LENGTH,
                            unique=True
                            )
    color = ColorField(verbose_name='Цвет',
                       unique=True,
                       help_text='Введите НЕХ-код'
                       )

    slug = models.SlugField(verbose_name='Slug',
                            max_length=MAX_LENGTH,
                            unique=True
                            )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=MAX_LENGTH
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_unit'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор'
                               )
    name = models.CharField(verbose_name='Название рецепта',
                            max_length=MAX_LENGTH
                            )
    image = models.ImageField(verbose_name='Картинка',
                              upload_to='recipes/'
                              )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Игредиенты',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    cooking_time = models.PositiveIntegerField(
        "Время приготовления блюда в минутах",
        validators=[
            MinValueValidator(
                1, "Время приготовления блюда должно" " быть не менее 1 минуты"
            ),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиенты в рецепте'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            validators.MinValueValidator(MIN_LIMIT),
            validators.MaxValueValidator(MAX_LIMIT),
        ]
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Ингредиенты для приготовления'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (
            f'{self.recipe.name}: '
            f'{self.ingredient.name} - '
            f'{self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class Favorites(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorite_recipe',
                               verbose_name='Рецепт',
                               )
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorite_user',
                             verbose_name='Пользователь'
                             )

    class Meta:
        ordering = ['user']
        verbose_name = 'Рецепт в Избранном'
        verbose_name_plural = 'Рецепты в Избранном'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe.name} в избранном у {self.user}'


class Shopping_cart(models.Model):
    Ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиент в кщрзине', blank=True
    )
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_user',
                             verbose_name='Пользователь'
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shopping_recipe',
                               verbose_name='Рецепт')

    class Meta:
        ordering = ['user']
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины покупок пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
