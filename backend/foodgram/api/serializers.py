import base64
from rest_framework.fields import IntegerField
from django.core.files.base import ContentFile
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework.serializers import (
    CharField,
    CurrentUserDefault,
    HiddenField,
    ImageField,
    ModelSerializer,
    PrimaryKeyRelatedField,
)


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientSerializer(ModelSerializer):
    name = CharField(source="ingredient.name")
    measurement_unit = CharField(source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_ingredient"
    )

    class Meta:
        model = Recipe
        fields = "__all__"


class RecipeIngredientCreateSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )
    # id = IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeCreateSerializer(ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    author = HiddenField(
        default=CurrentUserDefault()
    )  # add current user as author (only id)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            "name",
            "image",
            "cooking_time",
            "text",
            "tags",
            "ingredients",
            "author",
        )

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        instance = super().create(validated_data)

        for ingredient_data in ingredients:
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient_data["ingredient"],
                amount=ingredient_data["amount"],
            ).save()

        return instance

    # def to_representation(self, instance):
    #     return super().to_representation(instance)
