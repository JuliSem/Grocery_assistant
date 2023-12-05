from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from api.validators import (
    validate_name_recipe,
    validate_tag_slug
)
from foodgram.constants import (
    COLOR_MAX_LENGTH,
    INGREDIENT_NAME,
    INGREDIENT_MEASUREMENT_UNIT,
    RECIPE_NAME,
    SLUG_MAX_LENGTH,
    TAG_NAME
)
from users.models import User


class Tag(models.Model):
    """Модель для тэгов."""

    name = models.CharField(verbose_name='Название тэга',
                            max_length=TAG_NAME,
                            unique=True)
    color = ColorField(verbose_name='Цвет в HEX',
                       max_length=COLOR_MAX_LENGTH)
    slug = models.SlugField(verbose_name='Уникальный слаг',
                            max_length=SLUG_MAX_LENGTH,
                            validators=(validate_tag_slug,),
                            unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для ингредиента."""

    name = models.CharField(verbose_name='Название ингредиента',
                            max_length=INGREDIENT_NAME)
    measurement_unit = models.CharField(verbose_name='Единица измерения',
                                        max_length=INGREDIENT_MEASUREMENT_UNIT)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_name_measurement_unit'
        )]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель для рецептов."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=RECIPE_NAME,
        validators=(validate_name_recipe,)
    )
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления(в мин)',
        validators=[MinValueValidator(limit_value=1,
                                      message='Минимальное время '
                                              'приготовления - 1 мин!'),
                    MaxValueValidator(limit_value=1500,
                                      message='Время приготовления не должно '
                                              'превышать 1500 мин!')]
    )
    pub_date = models.DateField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('pub_date', )

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """Модель ингредиентов в рецепте."""

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент в рецепте',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        default=1,
        validators=[
            MinValueValidator(limit_value=1,
                              message='Количество ингредиента '
                                      'не должно быть меньше 1!'),
            MaxValueValidator(limit_value=10000,
                              message='Количество ингредиентов '
                                      'не должно быть больше 10000!')
        ]
    )

    class Meta:
        default_related_name = 'ingredients_recipe'
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_in_recipe'
            ),
            models.CheckConstraint(
                check=models.Q(amount__gte=1),
                name='amount_gte_1'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class ModelFavoriteOrShoppingCart(models.Model):
    """Абстрактная модель для избранного и списка покупок."""

    recipe = models.ForeignKey(Recipe,
                               verbose_name='Рецепты',
                               on_delete=models.CASCADE)
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE)

    class Meta:
        abstract = True
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_favorite_shopping_cart'
        )]


class ShoppingCart(ModelFavoriteOrShoppingCart):
    """Модель для списка покупок."""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'

    def __str__(self):
        return f'Список покупок {self.user}'


class Favorite(ModelFavoriteOrShoppingCart):
    """Модель для избранного."""

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'in_favorite'
