from django import forms
from django.contrib import admin


from recipes.models import (
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tag
)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('ingredient',
                    'recipe',
                    'amount')
    list_display_links = ('recipe',)
    list_filter = ('ingredient', 'recipe')
    search_fields = ('ingredient',)


class RecipeForm(forms.ModelForm):
    """Обязательные поля при создании рецепта."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredients', 'tags'].required = True

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    form = RecipeForm
    list_display = ('pub_date',
                    'author',
                    'name',
                    'get_ingredients',
                    'cooking_time',
                    'in_favorite')
    list_display_links = ('name',)
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)
    readonly_fields = ('in_favorite',)

    @admin.display(description='Количество добавлений в избранное')
    def in_favorite(self, obj):
        """Вычисляет количество добавлений рецепта в избранное."""
        return obj.in_favorite.all().count()

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        """Выводит список ингредиентов."""
        return ', '.join(
            [ingredients.name for ingredients in obj.ingredients.all()]
        )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe',
                    'user')
    list_filter = ('recipe', 'user')
    search_fields = ('user',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'color',
                    'slug')
    list_display_links = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)
