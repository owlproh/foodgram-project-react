from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Класс модели Пользователя"""
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        validators=[RegexValidator(
            regex=r'[\w.@+-]+$',
            message='Логин содержит недопустимый символ'
        )],
        verbose_name='Логин',
        help_text='Введите желаемый логин для регистрации',
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',
        help_text='Помните о надежности пароля:)'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Как к Вам обращаться?'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Ваша фамилия, если имеется'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='email',
        help_text='Введите Ваш email'
    )
    is_stuff = models.BooleanField(
        default=False,
        verbose_name='Статус администратора'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password'
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Subscription(models.Model):
    """Класс модели Подписок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text=('Выберите пользователя, '
                   'кому нужно оформить подписку на автора')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Выберите автора, на кого нужно оформить подписку'
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'
            ),
        ]

    def __str__(self):
        return f'Пользователь <<{self.user}>> подписан на: {self.author}'
