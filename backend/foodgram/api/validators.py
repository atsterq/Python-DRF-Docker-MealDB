from django.forms import ValidationError
from django.shortcuts import get_object_or_404

from backend.foodgram.recipes.models import Ingredient


def validate_ingredients(self, value):
    ingredients = value
    if not ingredients:
        raise ValidationError("At least one ingredient should be added.")

    ingredients_list = []
    for item in ingredients:
        ingredient = get_object_or_404(Ingredient, id=item["id"])
        if ingredient in ingredients_list:
            raise ValidationError("Ingredients can't be duplicated.")
        if int(item["amount"]) <= 0:
            raise ValidationError("Ingredient amount should be more than 0.")
        ingredients_list.append(ingredient)
    return value
