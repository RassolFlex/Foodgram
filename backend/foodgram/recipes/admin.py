from django.contrib import admin
from django.utils.safestring import mark_safe

from foodgram.constants import LIST_PER_PAGE
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)


class BaseAdmin(admin.ModelAdmin):
    """Администрирование базовых моделей."""

    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = LIST_PER_PAGE


class IngredientInline(admin.TabularInline):
    """Инлайн для добавления ингредиентов."""

    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(BaseAdmin):
    """Администрирование рецептов."""

    list_filter = ('author', 'tags')
    inlines = (IngredientInline,)

    def get_list_display(self, request):
        return self.list_display + (
            'author',
            'get_tags',
            'get_ingredients',
            'get_favorite_count',
            'get_image',
        )

    def get_list_searchable_fields(self, request):
        return self.search_fields + ('author', 'tags')

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        ingredients = []
        for ingredient in obj.ingredients.all():
            amount = RecipeIngredient.objects.get(
                recipe=obj, ingredient=ingredient
            ).amount
            ingredients.append(
                f'{ingredient.name}, '
                f'{amount}, '
                f'{ingredient.measurement_unit}'
            )
        return ingredients

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        return obj.favoriterecipe_recipe.count()

    @admin.display(description='Изображение')
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">')


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    """Администрирование тегов."""

    list_filter = ('name', 'color', 'slug')

    def get_list_display(self, request):
        return self.list_display + ('color', 'slug')

    def get_list_searchable_fields(self, request):
        return self.search_fields + ('color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(BaseAdmin):
    """Администрирование ингредиентов."""

    list_filter = ('measurement_unit',)

    def get_list_display(self, request):
        return self.list_display + ('measurement_unit',)

    def get_list_searchable_fields(self, request):
        return self.search_fields + ('measurement_unit',)


class CommonRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_per_page = LIST_PER_PAGE


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(CommonRecipeAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(CommonRecipeAdmin):
    pass
