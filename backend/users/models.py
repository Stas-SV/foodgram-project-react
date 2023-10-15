
from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_username

# Create your models here.
class User(AbstractUser):

    email = models.EmailField(
        max_length=200,
        verbose_name='Email',
        unique=True
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Логин',
        unique=True,
        validators=(validate_username,)
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )

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
