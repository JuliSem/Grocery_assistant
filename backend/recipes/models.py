from django.core.validators import MinValueValidator
from django.db import models

from api.validators import (
    validate_tag_color,
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
    color = models.CharField(verbose_name='Цвет в HEX',
                             max_length=COLOR_MAX_LENGTH,
                             validators=(validate_tag_color,))
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
        max_length=RECIPE_NAME
    )
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления(в мин)',
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

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
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента',
        default=1,
        validators=[MinValueValidator(1)]
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


class ShoppingCart(models.Model):
    """Модель для списка покупок."""

    recipe = models.ForeignKey(Recipe,
                               verbose_name='Рецепты',
                               related_name='shopping_cart',
                               on_delete=models.CASCADE
                               )
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_recipe_in_shopcart'
        )]

    def __str__(self):
        return f'Список покупок {self.user}'


class Favorite(models.Model):
    """Модель для избранного."""

    recipe = models.ForeignKey(Recipe,
                               verbose_name='Рецепты',
                               related_name='in_favorite',
                               on_delete=models.CASCADE)
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_recipe_in_favorite'
        )]
