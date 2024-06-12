from rest_framework import serializers

from recipes.models import Recipe, User
from users.models import Follow


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


class FoodgramUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        request = self.context['request']
        return (request
                and request.user.is_authenticated
                and obj.following.filter(
                    follower=request.user
                ).exists())


class FollowSerializer(FoodgramUserSerializer):
    """Сериализатор для списка подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(default=0)

    class Meta(FoodgramUserSerializer.Meta):
        model = FoodgramUserSerializer.Meta.model
        fields = (FoodgramUserSerializer.Meta.fields
                  + ('recipes', 'recipes_count'))
        read_only_fields = ('username', 'email', 'first_name', 'last_name')

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        limit = self.context['request'].query_params['recipes_limit']
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except ValueError:
                raise serializers.ValidationError({
                    'error': 'recipes_limit должен быть числом'
                })
        return RecipeShortSerializer(
            recipes,
            many=True,
            context=self.context
        ).data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки."""

    class Meta:
        model = Follow
        fields = ('following', 'follower')

    def validate(self, data):
        follower = data.get('follower')
        following = data.get('following')
        if follower == following:
            raise serializers.ValidationError({
                'error': 'Нельзя подписаться на самого себя'
            })
        if following.following.filter(follower=follower).exists():
            raise serializers.ValidationError({
                'error': 'Вы уже подписаны на этого пользователя'
            })
        return data

    def to_representation(self, instance):
        return FollowSerializer(
            instance.following,
            context=self.context
        ).data
