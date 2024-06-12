from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.paginations import PageLimitPaginator
from api.recipes.filters import RecipeFilter, SearchIngredientFilter
from api.recipes.permissions import IsAuthorOrReadOnly
from api.recipes.serializers import (FavoriteRecipeSerializer,
                                     IngredientSerializer,
                                     RecipeCreateSerializer, RecipeSerializer,
                                     ShoppingCartSerializer, TagSerializer)
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление рецептов."""

    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'ingredients'
    )
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PageLimitPaginator
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    filterset_fields = ('name', 'author')
    search_fields = ('name',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @staticmethod
    def object_create(serualizer, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        serualizer = serualizer(
            data=data, context={'request': request}
        )
        serualizer.is_valid(raise_exception=True)
        serualizer.save()
        return Response(serualizer.data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, pk):
        return self.object_create(
            FavoriteRecipeSerializer, request, pk
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        favorite_oject = FavoriteRecipe.objects.filter(
            user=request.user, recipe=pk
        )
        if favorite_oject.exists():
            favorite_oject.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return self.object_create(
            ShoppingCartSerializer, request, pk
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        shopping_cart_oject = ShoppingCart.objects.filter(
            user=request.user, recipe=pk
        )
        if shopping_cart_oject.exists():
            shopping_cart_oject.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        data = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values('ingredient__name', 'ingredient__measurement_unit',).annotate(
            amount=Sum('amount')
        ).order_by('ingredient__name')
        output = ''
        for ingredient in data:
            output += (f'{ingredient["ingredient__name"]}, '
                       f'{ingredient["amount"]} - '
                       f'{ingredient["measurement_unit"]}\n')
        return FileResponse(
            output.encode('utf-8'),
            as_attachment=True,
            filename='shopping_cart.txt'
        )


class ReadListViewSet(viewsets.ReadOnlyModelViewSet):
    """Миксин для тегов и ингредиентов."""

    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class TagViewSet(ReadListViewSet):
    """Представление тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadListViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = SearchIngredientFilter
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
