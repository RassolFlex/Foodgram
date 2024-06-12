from django.db.models import Count
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.paginations import PageLimitPaginator
from api.users.serializers import FollowSerializer, SubscribeSerializer
from recipes.models import User
from users.models import Follow


class FoodgramUserViewSet(UserViewSet):
    """Представление пользователя."""

    pagination_class = PageLimitPaginator

    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    @action(methods=('POST',),
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, *args, **kwargs):
        data = {
            'follower': request.user.id,
            'following': kwargs['id'],
        }
        serializer = SubscribeSerializer(
            context={'request': request},
            data=data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscription(self, request, *args, **kwargs):
        user = self.get_object()
        subscriber = request.user
        obj = Follow.objects.filter(follower=subscriber, following=user)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Вы не подписаны', status=status.HTTP_400_BAD_REQUEST)

    @action(methods=('GET',),
            detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        subscriber = request.user
        queryset = User.objects.filter(
            following__follower=subscriber
        ).annotate(recipes_count=Count('recipes'))
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(page,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)
