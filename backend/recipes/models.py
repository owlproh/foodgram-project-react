from django.db import models
from users.models import User
from foodgram.settings import TEXT_SL
from django.core.validators import MinValueValidator, RegexValidator


class Tag(models.Model):
    """Класс модели Тегов"""
    name = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        verbose_name='Имя тега',
        help_text='Введите название тега',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Hex-code цвета',
        help_text='Введите Hex-код нужного цвета',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Слаг тега содержит недопустимый символ'
        )],
        verbose_name='slug тега',
        help_text='Введите сокращенние для тега',
    )

    class Meta:
        verbose_name = 'Тег',
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, ({self.slug[:TEXT_SL]})'


class Ingredient(models.Model):
    """Класс модели Ингредиентов"""
    name = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name='Название',
        help_text='Введите название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=10,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения для ингредиента',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:TEXT_SL]


class Recipe(models.Model):
    """Класс модели Рецептов"""
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Ingredient_to_Recipe',
        related_name='recipes',
        verbose_name='Ингридиенты',
        help_text='Укажите ингредиенты для блюда',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        help_text='Укажите подходящие теги',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение',
        help_text='Добавьте фото к Вашему рецепту',
    )
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название',
        help_text='Введите название блюда',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                1,
                message='Время приготовления не может быть меньше 1'
            ),
        ],
        help_text='Введите время приготовления блюда в минутах',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:TEXT_SL]


class Ingredient_to_Recipe(models.Model):
    """Класс вспомогательной модели для связи ингредиентов и рецептов"""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиент',
        help_text='Выберите ингредиент(ы)'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт',
        help_text='Укажите для какого блюда вы выбрали ингредиент(ы)'
    )
    cnt = models.PositiveIntegerField(
        verbose_name='Количество ингредиента',
        validators=[
            MinValueValidator(
                1,
                message='Количество ингредиента не может быть нулевым'
            ),
        ],
        help_text='Введите количество ингредиента(ов), для данного рецепта'
    )

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Соответствие ингредиентов и рецептов'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ItR'
            ),
        )

    def __str__(self):
        return (f'В рецепте <<{self.recipe.name}>>'
                f'следующий(ие) ингредиент(ы): {self.ingredient.name}'
                f'({self.cnt})')


class Shopping_Cart(models.Model):
    """Класс модели Корзины"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
        help_text='Выберите рецепт(ы)'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )

    class Meta:
        verbose_name = 'Список покупок пользователя'
        verbose_name_plural = 'Списки покупок пользователей'
        ordering = ('user',)
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_cart'
            ),
        )

    def __str__(self):
        return (f'Ингредиенты для рецепта {self.recipe.name}'
                f'добавлены в список покупок пользователя {self.user}')


class Favorite(models.Model):
    """Класс модели Избранных"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт',
        help_text='Выберите рецепт(ы)'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_fav'
            ),
        )

    def __str__(self):
        return (f'Рецепт <<{self.recipe}>> добавлен в избранное'
                f'у пользователя {self.user}')
