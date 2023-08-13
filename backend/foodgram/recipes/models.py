from django.contrib.auth import get_user_model
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey,
    ImageField,
    ManyToManyField,
    Model,
    PositiveIntegerField,
    SlugField,
    TextField,
    UniqueConstraint,
)

User = get_user_model()


class Tag(Model):
    name = CharField(max_length=200, unique=True)
    color = CharField(max_length=7, unique=True)
    slug = SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = "Tag"
        ordering = ("slug",)
        constraints = [UniqueConstraint(fields=["slug"], name="unique_slug")]

    def __str__(self):
        return self.name


class Ingredient(Model):
    name = CharField(max_length=200, db_index=True)
    measurement_unit = CharField(max_length=200)


class Recipe(Model):
    tags = ManyToManyField(Tag)
    name = CharField(max_length=200)
    cooking_time = PositiveIntegerField()
    text = TextField()
    author = ForeignKey(User, on_delete=CASCADE, related_name="recipes")
    ingredients = ManyToManyField(
        "Ingredient",
        through="RecipeIngredient",
        through_fields=("recipe", "ingredient"),
        related_name="recipes",
    )
    image = ImageField(upload_to="recipes/images/", null=True, default=None)
    pub_date = DateTimeField("Publication date", auto_now_add=True)

    class Meta:
        verbose_name = "Recipe"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name


class RecipeIngredient(Model):
    recipe = ForeignKey(
        Recipe, on_delete=CASCADE, related_name="recipe_ingredient"
    )
    ingredient = ForeignKey(
        Ingredient, on_delete=CASCADE, related_name="recipe_ingredient"
    )
    amount = PositiveIntegerField()

    class Meta:
        verbose_name = "Recipe ingredients"
        constraints = [
            UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient",
            )
        ]


class Favorite(Model):
    user = ForeignKey(User, on_delete=CASCADE, related_name="favorite")
    recipe = ForeignKey(Recipe, on_delete=CASCADE, related_name="favorite")

    class Meta:
        verbose_name = "Favorite recipes"
        constraints = [
            UniqueConstraint(
                fields=["recipe", "user"],
                name="unique_user_favorite",
            )
        ]


class ShoppingCart(Model):
    user = ForeignKey(User, on_delete=CASCADE, related_name="shopping_cart")
    recipe = ForeignKey(
        Recipe, on_delete=CASCADE, related_name="shopping_cart"
    )

    class Meta:
        verbose_name = "Shopping cart"
        constraints = [
            UniqueConstraint(
                fields=["recipe", "user"],
                name="unique_user_shopping_cart",
            )
        ]
