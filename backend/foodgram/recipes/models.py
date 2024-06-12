from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram.constants import (LENGTH_FOR_FIELD_RECIPES, MAX_VALUE, MIN_VALUE,
                                SLICE)

User = get_user_model()


class NameBaseModel(models.Model):
    """Базовая модель."""

    name = models.CharField(
        max_length=LENGTH_FOR_FIELD_RECIPES,
        verbose_name='Название',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[:SLICE]


class Tag(NameBaseModel):
    """Модель тега."""

    color = ColorField(
        verbose_name='Цвет в формате HEX',
        unique=True,
    )
    slug = models.SlugField(
        max_length=LENGTH_FOR_FIELD_RECIPES,
        verbose_name='Слаг',
        unique=True,
    )

    class Meta(NameBaseModel.Meta):
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        default_related_name = 'tag'


class Ingredient(NameBaseModel):
    """Модель ингридиента."""

    measurement_unit = models.CharField(
        max_length=LENGTH_FOR_FIELD_RECIPES,
        verbose_name='Единица измерения',
    )

    class Meta(NameBaseModel.Meta):
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        default_related_name = 'ingredient'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit',
            ),
        )


class Recipe(NameBaseModel):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингридиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                MIN_VALUE,
                f'Значение должно быть больше {MIN_VALUE}'
            ),
            MaxValueValidator(
                MAX_VALUE,
                f'Значение должно быть меньше {MAX_VALUE}'
            ),
        )
    )

    class Meta(NameBaseModel.Meta):
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipe'


class RecipeIngredient(models.Model):
    """Модель ингридиента рецепта."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                MIN_VALUE,
                f'Значение должно быть больше {MIN_VALUE}'
            ),
            MaxValueValidator(
                MAX_VALUE,
                f'Значение должно быть меньше {MAX_VALUE}'
            ),
        )
    )

    class Meta:
        verbose_name = 'Ингридиент рецепта'
        verbose_name_plural = 'Ингридиенты рецепта'
        default_related_name = 'recipe_ingredient'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        )

    def __str__(self):
        return self.ingredient.name[:SLICE]


class UserRecipeBaseModel(models.Model):
    """Абстрактная модель для избранного и списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s_recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(class)s_unique_user_recipe',
            ),
        )

    def __str__(self):
        return self.recipe.name[:SLICE]


class FavoriteRecipe(UserRecipeBaseModel):
    """Модель списка избранных рецептов."""

    class Meta(UserRecipeBaseModel.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(UserRecipeBaseModel):
    """Модель списка покупок."""

    class Meta(UserRecipeBaseModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
