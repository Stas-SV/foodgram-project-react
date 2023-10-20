
from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_LENGTH = 200
MAX_STRING = 150


class User(AbstractUser):
    email = models.EmailField(
        unique=True
    )
    password = models.CharField(
        'Пароль',
        max_length=MAX_STRING,
    )
    first_name = models.CharField(
        max_length=MAX_STRING,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(User,
                             verbose_name='Подписчик',
                             on_delete=models.CASCADE,
                             related_name='subscriber')
    author = models.ForeignKey(User,
                               verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='subscribing')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return self.user
