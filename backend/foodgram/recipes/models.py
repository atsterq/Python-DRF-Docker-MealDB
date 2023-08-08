from django.contrib.auth import get_user_model
from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
    ImageField,
    ManyToManyField,
    Model,
    PositiveIntegerField,
    SlugField,
    TextField,
)

User = get_user_model()


class Tag(Model):
    name = CharField(max_length=200, unique=True)
    color = CharField(max_length=7, unique=True)
    slug = SlugField(max_length=200, unique=True)


class Recipe(Model):
    tags = ManyToManyField(Tag)
    name = CharField(max_length=200)
    cooking_time = PositiveIntegerField()
    text = TextField()
    author = ForeignKey(User, on_delete=CASCADE)
    ingredients = ManyToManyField(
        "Ingredient",
        through="RecipeIngredient",
        through_fields=("recipe", "ingredient"),
    )
    image = ImageField(upload_to="recipes/images/", null=True, default=None)


class Ingredient(Model):
    name = CharField(max_length=200, db_index=True)
    measurement_unit = CharField(max_length=200)


class RecipeIngredient(Model):
    recipe = ForeignKey(
        Recipe, related_name="recipe_ingredient", on_delete=CASCADE
    )
    ingredient = ForeignKey(Ingredient, on_delete=CASCADE)
    amount = PositiveIntegerField()
