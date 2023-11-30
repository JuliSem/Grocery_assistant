from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from .paginations import LimitPagination
from .filters import IngredientSearch, RecipeFilter
from .permissions import IsAuthorOrReadOnly, ReadOnly
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    ProfileUserSerializer,
    RecipeSerializer,
    RecipeListSerializer,
    ShoppingCartSerializer,
    SubscribeListSerializer,
    SubscribeSerializer,
    TagSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import User, Subscribe


class UserViewSet(UserViewSet):
    """Viewset для подписок."""

    queryset = User.objects.all()
    serializer_class = ProfileUserSerializer
    pagination_class = LimitPagination
    permission_classes = (IsAuthenticated, )

    @action(methods=['GET'], detail=False)
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeListSerializer(page,
                                             many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data={'user': user.id, 'author': id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = Subscribe.objects.filter(user=user, author=author)
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Вы не подписаны на данного пользователя!'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TagListViewSet(ReadOnlyModelViewSet):
    """ViewSet для получения тега/ тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientListViewSet(ReadOnlyModelViewSet):
    """ViewSet для получения ингредиента/ ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearch, )


class RecipeViewSet(ModelViewSet):
    """ViewSet для рецепта."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    filterset_fields = ('author',
                        'is_favorited',
                        'is_in_shopping_cart',
                        'tags')
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (ReadOnly(),)
        return super().get_permissions()

    @staticmethod
    def method_for_post_action(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def method_for_delete_action(request, pk, model):
        recipe = get_object_or_404(Recipe, id=pk)
        model_instance = get_object_or_404(
            model, user=request.user, recipe=recipe
        )
        model_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk):
        return self.method_for_post_action(request, pk, FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.method_for_delete_action(request, pk, Favorite)

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk):
        return self.method_for_post_action(
            request, pk, ShoppingCartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.method_for_delete_action(request, pk, ShoppingCart)

    @action(
        detail=False, methods=['get'], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientAmount.objects
            .filter(recipe__shopping_cart__user=request.user)
            .values('ingredient')
            .annotate(amount_of_ingredient=Sum('amount'))
            .values_list('ingredient__name',
                         'ingredient__measurement_unit',
                         'amount_of_ingredient')
        )
        shopping_list = (('{} ({}) - {}'.format(*ingredient) + '\n')
                         for ingredient in ingredients)

        return FileResponse('\n'.join(shopping_list),
                            as_attachment=True,
                            filename='shopping_cart.txt',
                            status=status.HTTP_200_OK,
                            content_type='text/plain')
