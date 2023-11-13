import csv
import os

from django.core.management import BaseCommand

from foodgram import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    """Загрузка ингредиентов из csv файла(в директории data) 
    в базу данных."""

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv')
        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
            print('Импорт данных успешно выполнен!')