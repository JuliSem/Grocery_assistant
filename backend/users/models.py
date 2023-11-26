from django.contrib.auth.models import AbstractUser
from django.db import models

from api.validators import validate_username
from foodgram.constants import (
    EMAIL_MAX_LENGTH,
    USER_MAX_LENGTH
)


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    email = models.EmailField(verbose_name='Электронная почта',
                              max_length=EMAIL_MAX_LENGTH,
                              blank=False,
                              unique=True)
    username = models.CharField(verbose_name='Пользователь',
                                validators=(validate_username,),
                                max_length=USER_MAX_LENGTH,
                                blank=False,
                                unique=True)
    first_name = models.CharField(verbose_name='Имя',
                                  max_length=USER_MAX_LENGTH,
                                  blank=False
                                  )
    last_name = models.CharField(verbose_name='Фамилия',
                                 max_length=USER_MAX_LENGTH,
                                 blank=False
                                 )
    password = models.CharField(verbose_name='Пароль',
                                max_length=USER_MAX_LENGTH,
                                blank=False)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Subscribe(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(fields=['user', 'author'],
                                               name='unique_user_author')]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
