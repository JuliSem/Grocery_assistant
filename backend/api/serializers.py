import base64

from django.core.files.base import ContentFile
from django.db.transaction import atomic
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import (
    UniqueTogetherValidator
)

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import Subscribe, User


class SignUpSerializer(UserCreateSerializer):
    """Serializer для регистрации пользователя."""

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class ProfileUserSerializer(UserSerializer):
    """Serializer для модели пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user,
                                        author=obj).exists()


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Serializer для получения сокращённого вида рецепта
    (при получении списка подписок, добавлении в список покупок)."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeListSerializer(serializers.ModelSerializer):
    """Serializer для получения списка подписок."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.ReadOnlyField(source='recipes.count')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes(self, object):
        request = self.context.get('request')
        context = {'request': request}
        recipe_limit = request.query_params.get('recipe_limit')
        queryset = object.recipes.all()
        if recipe_limit:
            queryset = queryset[:int(recipe_limit)]
        return ShortRecipeSerializer(queryset, context=context, many=True).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user,
                                        author=obj.id).exists()


class SubscribeSerializer(serializers.ModelSerializer):
    """Serializer для создания подписки."""

    class Meta:
        model = Subscribe
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, data):
        user = self.context.get('request').user
        author = data['author']
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться сами на себя!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeSerializer(
            instance.author, context={'request': request}
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Serializer для модели Тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer для модели Ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AddIngredientSerializer(serializers.ModelSerializer):
    """Serializer для добавления ингредиентов в рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')

    def validate(self, data):
        if data['amount'] < 1:
            raise serializers.ValidationError(
                'Количество ингредиентов не должно быть меньше 1!'
            )
        return data

    def create(self, validated_data):
        return IngredientAmountSerialiser.objects.create(
            ingredient=validated_data.get('id'),
            amount=validated_data.get('amount')
        )


class Base64ImageField(serializers.ImageField):
    """Serializer для изображений, закодированных в Base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgestr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgestr), name='image.' + ext)
            return super().to_internal_value(data)


class IngredientAmountSerialiser(serializers.ModelSerializer):
    """Serializer для получения ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Serializer для получения рецепта/ рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = ProfileUserSerializer(read_only=True)
    ingredients = IngredientAmountSerialiser(
        many=True,
        source='ingredients_recipe',
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user,
                                       recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user,
                                           recipe__id=obj.id).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer для создания рецепта."""

    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time')

    def create_ingredients(self, recipe, ingredients):
        IngredientAmount.objects.bulk_create([
            IngredientAmount(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient['id'],
            ) for ingredient in ingredients
        ])

    def validate(self, data):
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Нужно выбрать хотя бы один тег!'
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги не уникальны!'
            )
        ingredients = data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться!'
                )
            ingredients_list.append(ingredient_id)
        if data['cooking_time'] <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0!'
            )
        return data

    @atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = instance
        IngredientAmount.objects.filter(recipe=recipe).delete()
        self.create_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(instance, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer для списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')

    def validate(self, data):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if ShoppingCart.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(instance.recipe, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer для избранного."""

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')

    def validate(self, data):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user,
                                   recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(instance.recipe, context=context).data
