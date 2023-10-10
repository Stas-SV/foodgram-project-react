from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(verbose_name='Название',
                            max_length=200
                            )
    slug = models.SlugField(verbose_name='Slug',
                            max_length=200
                            )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Название ингредиента',
                            max_length=200
                            )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(verbose_name='Название рецепта',
                            max_length=200
                            )
    tags = models.ManyToManyField(Tag,
                                  verbose_name='Теги',
                                  related_name='recipes')
    ingredients = models.ManyToManyField(Ingredient,
                                         verbose_name='Игредиенты',
                                         related_name='recipes')
    text = models.TextField('Описание',
                            help_text='Введите введите описание рецепта'
                            )
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True
                                    )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор'
                               )
    image = models.ImageField('Картинка',
                              upload_to='recipes/',
                              blank=True
                              )

    def __str__(self):
        return self.name
