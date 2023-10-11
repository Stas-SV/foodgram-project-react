from django.contrib.auth import get_user_model
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

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Название ингредиента',
                            max_length=200
                            )
    measurements = models.CharField(verbose_name='Единица измерения',
                                    max_length=200,
                                    default='грамм'
                                    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор'
                               )
    name = models.CharField(verbose_name='Название рецепта',
                            max_length=200
                            )
    image = models.ImageField('Картинка',
                              upload_to='recipes/',
                              blank=True
                              )
    text = models.TextField('Описание',
                            help_text='Введите описание рецепта'
                            )
    ingredients = models.ManyToManyField(Ingredient,
                                         verbose_name='Игредиенты',
                                         related_name='recipes'
                                         )
    tags = models.ManyToManyField(Tag,
                                  verbose_name='Теги',
                                  related_name='recipes')
    time = models.PositiveSmallIntegerField(verbose_name='Время приготовления в минутах',
                                            default=1
                                            )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe_ingredients',
                               verbose_name='Рецепты'
                               )
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='recipe_ingredients',
                                   verbose_name='Ингредиент',
                                   )
    amount = models.PositiveIntegerField(verbose_name='Количество игредиентов',
                                         default=1
                                         )

    def __str__(self):
        return f'{self.ingredient.name} - {self.amount}'


class Favorite(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorites',
                               verbose_name='Рецепт',
                               )
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorites',
                             verbose_name='Пользователь'
                             )

    def __str__(self):
        return f'Рецепт {self.recipe.name} в избранном у {self.user}'


class ShoppingList(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='shopping_list',
                             verbose_name='Пользователь'
                             )
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shopping_list',
                               verbose_name='Рецепт')

    def __str__(self):
        return (
            f'Рецепт {self.recipe.name} в списке покупок у'
            f' {self.user}')
