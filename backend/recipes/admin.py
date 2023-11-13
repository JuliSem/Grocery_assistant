from django.contrib import admin


from recipes.models import (
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tag
)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('ingredient',
                    'recipe',
                    'amount')
    list_display_links = ('recipe',)
    list_filter = ('ingredient', 'recipe')
    search_fields = ('ingredient',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pub_date',
                    'author',
                    'name',
                    'cooking_time',
                    'in_favorite')
    list_display_links=('name',)
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)
    readonly_fields = ('in_favorite',)

    def in_favorite(self, obj):
        """Вычисляет количество добавлений рецепта в избранное."""
        return obj.in_favorite.all().count()

    in_favorite.short_description = 'Количество добавлений в избранное'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe',
                    'user')
    list_filter = ('recipe', 'user')
    search_fields = ('user',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'color',
                    'slug')
    list_display_links = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)

admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tag, TagAdmin)