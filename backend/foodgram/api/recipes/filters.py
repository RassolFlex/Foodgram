from django_filters import CharFilter, FilterSet, ModelMultipleChoiceFilter

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""

    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = CharFilter(method='get_favorite')
    is_in_shopping_cart = CharFilter(method='get_shopping')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_favorite(self, queryset, name, value):
        """Метод для фильтрации рецептов по избранному."""

        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favoriterecipe_recipe__user=self.request.user
            )
        return queryset

    def get_shopping(self, queryset, name, value):
        """Метод для фильтрации рецептов в списке покупок."""

        if value and self.request.user.is_authenticated:
            return queryset.filter(
                shoppingcart_recipe__user=self.request.user
            )
        return queryset


class SearchIngredientFilter(FilterSet):
    """Фильтр для поиска ингредиентов."""

    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
