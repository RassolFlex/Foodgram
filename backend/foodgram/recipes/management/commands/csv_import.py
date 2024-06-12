import csv
from os import path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError


class FileOpenException(Exception):
    """Вызов исключения при некорректном открытии файла."""
    pass


class Command(BaseCommand):
    def handle(self, **options):
        model_class = apps.get_model('recipes', 'ingredient')
        path_to_csv = path.join(
            settings.BASE_DIR,
            'data/ingredients.csv'
        )
        try:
            with open(path_to_csv, newline='', encoding='utf-8') as f:
                dataframe = csv.reader(f)
                for name_column, unit_column in dataframe:
                    try:
                        model_class.objects.get_or_create(
                            name=name_column,
                            measurement_unit=unit_column
                        )
                    except IntegrityError:
                        self.stdout.write(
                            f'Объект "ingredient" ID:'
                            f'{name_column.get("id")} уже существует'
                        )
                        continue
                self.stdout.write(
                    'Закончен импорт ингридиентов в базу данных'
                )
        except FileOpenException as error:
            self.stdout.write(f'Ошибка при открытии файла: {error}')
