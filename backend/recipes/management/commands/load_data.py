import csv
import os

from django.core.management import BaseCommand

from foodgram import settings
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Загрузка ингредиентов, тегов из csv файла(в директории data) 
    в базу данных."""

    def import_ingredients(self, file='ingredients.csv'):
        file_path = os.path.join(settings.BASE_DIR, 'data', file)
        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
            print('Импорт ингредиентов успешно выполнен!')

    def import_tags(self, file='tags.csv'):
        file_path = os.path.join(settings.BASE_DIR, 'data', file)
        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                Tag.objects.get_or_create(
                    name=row[0],
                    color=row[1],
                    slug=row[2] 
                )
            print('Импорт тегов успешно выполнен!')

    def handle(self, *args, **options):
        self.load_ingredients()
        self.load_tags()