from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.users.serializers import FoodgramUserSerializer
from foodgram.constants import MAX_VALUE, MIN_VALUE
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания связи ингредиента с рецептом."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE,
        error_messages={
            'min_value': f'Минимальное значение {MIN_VALUE}',
            'max_value': f'Максимальное значение {MAX_VALUE}',
        }
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для связи ингредиента с рецептом."""

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    author = FoodgramUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(allow_null=False, allow_empty_file=False)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredient', many=True
    )
    is_favorited = serializers.SerializerMethodField(default=False)
    is_in_shopping_cart = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context['request']
        return (request
                and request.user.is_authenticated
                and obj.favoriterecipe_recipe.filter(
                    user=request.user.id
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        return (request
                and request.user.is_authenticated
                and obj.shoppingcart_recipe.filter(
                    user=request.user.id
                ).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""

    image = Base64ImageField(allow_null=False, allow_empty_file=False)
    ingredients = IngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE,
        error_messages={
            'min_value': f'Минимальное значение {MIN_VALUE}',
            'max_value': f'Максимальное значение {MAX_VALUE}',
        }
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, attrs):
        ingredients = attrs.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'error': 'Необходимо добавить ингредиенты'
            })
        ingredient_list = [
            ingrediend['id'] for ingrediend in ingredients
        ]
        if len(set(ingredient_list)) != len(ingredient_list):
            raise serializers.ValidationError({
                'error': 'Ингредиенты не должны повторяться'
            })
        tags = attrs.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'error': 'Необходимо добавить теги'
            })
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError({
                'error': 'Теги не должны повторяться'
            })
        return attrs

    @staticmethod
    def create_ingredients(recipe, ingredients):
        recipe_ingredients = [RecipeIngredient(
            recipe=recipe,
            ingredient=ingredient_data['id'],
            amount=ingredient_data['amount']
        ) for ingredient_data in ingredients]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context.get('request').user,
                                       **validated_data)
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(recipe=instance, ingredients=ingredients)
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance=instance, context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для короткого отображения рецептов."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeUserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""

    class Meta:
        fields = (
            'user',
            'recipe'
        )

    def validate(self, attrs):
        if self.Meta.model.objects.filter(
            user=self.context.get('request').user,
            recipe=attrs.get('recipe')
        ).exists():
            raise serializers.ValidationError({
                'error': f'Рецепт уже добавлен в {self.Meta.model.__name__}'
            })
        return attrs

    def to_representation(self, instance):
        return RecipeShortSerializer(instance=instance.recipe).data


class FavoriteRecipeSerializer(RecipeUserSerializer):
    """Сериализатор избранных рецептов."""

    class Meta(RecipeUserSerializer.Meta):
        model = FavoriteRecipe


class ShoppingCartSerializer(RecipeUserSerializer):
    """Сериализатор списка покупок."""

    class Meta(RecipeUserSerializer.Meta):
        model = ShoppingCart
