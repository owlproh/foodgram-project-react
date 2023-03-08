import csv

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load data from csv file by the directory /data/'

    def handle(self, *args, **kwargs):
        with open(
            f'{settings.DIR_DATA_CSV}\\ingredients.csv',
            'r',
            encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file)
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in reader
            )

        self.stdout.write(self.style.SUCCESS(
            '==>>>Ингредиенты успешно загружены в БД<<<=='
        ))
