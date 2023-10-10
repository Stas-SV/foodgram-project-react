from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(verbose_name='Название рецепта',
                            max_length=200
                            )
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
