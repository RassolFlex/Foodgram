from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from foodgram.constants import LIST_PER_PAGE
from users.models import Follow

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Администрирование пользователя."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'get_recipes_count',
        'get_followers_count',
    )
    list_editable = (
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    list_filter = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_display_links = ('username', 'email',)
    list_per_page = LIST_PER_PAGE
    empty_value_display = 'Не указано'

    @admin.display(description='Кол-во рецептов')
    def get_recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Кол-во подписчиков')
    def get_followers_count(self, obj):
        return obj.following.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Администрирование подписок."""

    list_display = (
        'follower',
        'following',
    )
    search_fields = ('follower', 'following',)
    list_filter = ('follower', 'following',)
    list_display_links = ('follower', 'following',)
    list_per_page = LIST_PER_PAGE
    empty_value_display = 'Не указано'


admin.site.unregister(Group)
