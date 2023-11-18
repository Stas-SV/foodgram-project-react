import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag

COMMAND_TO_IMPORT = 'run'

PATH = Path.cwd() / 'recipes' / 'data'


def add_ingredient(row):
    ingredient = Ingredient(
        name=row['name'],
        measurement_unit=row['measurement_unit'],
    )
    ingredient.save()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(COMMAND_TO_IMPORT)

    def handle(self, *args, **kwargs):
        imported_models = {
            'ingredients.csv': add_ingredient,
        }

        for key in imported_models.keys():
            with open((f'{PATH}/{key}'), encoding='utf-8') as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    imported_models[key](row)
        self.stdout.write(self.style.SUCCESS('Игредиенты загружены успешно!'))

        data = [
            {'name': 'Завтрак', 'color': '#FCEB97', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#6BB324', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#DC6C14', 'slug': 'dinner'}]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(self.style.SUCCESS('Тэги загружены!'))
