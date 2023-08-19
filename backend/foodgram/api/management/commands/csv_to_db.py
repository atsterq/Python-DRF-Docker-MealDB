import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

PATH_TO_CSV = os.path.join(
    os.path.dirname(os.path.dirname(settings.BASE_DIR)),
    "data",
    "ingredients.csv",
)


class Command(BaseCommand):
    help = "Transfers data from csv file to database."

    def handle(self, *args, **options):
        self.stdout.write("Start of data transferring.")
        with open(str(PATH_TO_CSV), "r") as file:
            reader = csv.reader(file)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0], measurement_unit=row[1]
                )
        self.stdout.write(self.style.SUCCESS("Data is transferred!"))
