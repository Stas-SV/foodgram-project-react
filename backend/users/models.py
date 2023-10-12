
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):

    email = models.EmailField(
        max_length=200,
        verbose_name='Email',
        unique=True
    )
    username = models.CharField(
        max_length=200,
        verbose_name='Логин',
        unique=True,
    )
    first_name = models.CharField(
        max_length=200,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )


class Subscribe(models.Model):
    user = models.ForeignKey(User,
                             verbose_name='Подписчик',
                             on_delete=models.CASCADE,
                             related_name='subscriber')
    author = models.ForeignKey(User,
                               verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='subscribing')