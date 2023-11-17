from django_filters import rest_framework as filters

from recipes.models import Recipe

class RecipeFilter(filters.FilterSet):
    """Фильтры для рецептов."""
    
    author = filters.CharFilter(field_name='author')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'tags')
    
    def filter_is_favorited(self, queruset, name, value):
        if self.request.user.is_authenticated and value:
            return queruset.filter(favorite__user=self.request.user)
        return queruset
    
    def filter_is_in_shopping_cart(self, queruset, name, value):
        if self.request.user.is_authenticated and value:
            return queruset.filter(shopping_cart__user=self.request.user)
        return queruset