from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models

from foodgram.constants import (LENGTH_FOR_FIELD_EMAIL, LENGTH_FOR_FIELD_USERS,
                                SLICE)


class FoodgramUser(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'Юзернейм',
        max_length=LENGTH_FOR_FIELD_USERS,
        validators=(username_validator,),
        unique=True
    )
    first_name = models.CharField(
        'Имя', max_length=LENGTH_FOR_FIELD_USERS
    )
    last_name = models.CharField(
        'Фамилия', max_length=LENGTH_FOR_FIELD_USERS
    )
    email = models.EmailField(
        'email address', max_length=LENGTH_FOR_FIELD_EMAIL, unique=True
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:SLICE]


class Follow(models.Model):

    follower = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('follower', 'following'),
                name='unique_follow',
            ),
        )

    def __str__(self):
        return f'{self.follower} подписан на {self.following}'

    def clean(self):
        if self.follower == self.following:
            raise ValidationError('Нельзя подписаться на самого себя')
        super().save(self)
