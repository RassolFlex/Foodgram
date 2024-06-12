from django.core.management.base import BaseCommand
from slugify import slugify

from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, **options):
        tags = {
            'Завтрак': '#7FFF8D',
            'Обед': '#FFD700',
            'Ужин': '#FF6347'
        }
        try:
            for tag in tags:
                Tag.objects.get_or_create(
                    name=tag,
                    color=tags[tag],
                    slug=slugify(tag)
                )
        except Exception as error:
            self.stdout.write(f'Error: {error}')
        self.stdout.write('Теги успешно добавлены!')
