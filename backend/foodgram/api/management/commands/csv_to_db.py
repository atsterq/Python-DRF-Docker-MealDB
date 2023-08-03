import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

INGREDIENTS_CSV = os.path.join(
    os.path.dirname(os.path.dirname(settings.BASE_DIR)),
    "data",
    "ingredients.csv",
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(str(INGREDIENTS_CSV), "r", newline="") as file:
            reader = csv.DictReader(file, delimiter=",")
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0], measurement_unit=row[1] # там нет заголовков
                )
        self.stdout.write(self.style.SUCCESS("Data is transferred"))
