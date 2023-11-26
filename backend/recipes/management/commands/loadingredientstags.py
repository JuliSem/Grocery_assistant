import csv
import os

from django.core.management import BaseCommand

from foodgram import settings
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Загрузка ингредиентов, тегов из csv файла(в директории data)
    в базу данных."""

    def handle(self, *args, **options):
        ingredients_file_path = os.path.join(
            settings.BASE_DIR, 'data', 'ingredients.csv'
        )
        with open(ingredients_file_path, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
            self.stdout.write('Импорт ингредиентов успешно выполнен!')

        tags_file_path = os.path.join(settings.BASE_DIR, 'data', 'tags.csv')
        with open(tags_file_path, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                Tag.objects.get_or_create(
                    name=row[0],
                    color=row[1],
                    slug=row[2]
                )
            self.stdout.write('Импорт тегов успешно выполнен!')
