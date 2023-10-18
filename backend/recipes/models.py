from django.contrib.auth import get_user_model
from django.core import validators
from django.core.validators import MinValueValidator
from django.db import models
from colorfield.fields import ColorField

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(verbose_name='Название',
                            max_length=200
                            )
    color = ColorField(verbose_name='Цвет',
                       format='hex',
                       default='#49B64E')

    slug = models.SlugField(verbose_name='Slug',
                            max_length=200
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
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        default='грамм'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор'
                               )
    name = models.CharField(verbose_name='Название рецепта',
                            max_length=200
                            )
    image = models.ImageField(verbose_name='Картинка',
                              upload_to='recipes/',
                              blank=True,
                              null=True,
                              default=None
                              )
    text = models.TextField('Описание',
                            null=True,
                            blank=True,
                            default=None
                            )
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
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(32000),
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True,
        null=True,
        blank=True,
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
    amount = models.PositiveIntegerField(
        verbose_name='Количество игредиентов',
        validators=(MinValueValidator(
            1,
            message='Минимальное количество 1'),
        ),
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Ингредиенты для приготовления'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_combination'
            )
        ]

    def __str__(self):
        return f'{self.ingredient.name} - {self.amount}'


class Favorite(models.Model):
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
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping_cart')
        ]

    def __str__(self):
        return (
            f'Рецепт {self.recipe.name} в списке покупок у'
            f' {self.user}')
