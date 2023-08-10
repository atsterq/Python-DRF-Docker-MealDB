import base64

from django.core.files.base import ContentFile
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework.serializers import (
    CharField,
    CurrentUserDefault,
    HiddenField,
    ImageField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    # SerializerMethodField,
)
from users.models import Subscription, User


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"


class UserSerializer(ModelSerializer):
    # recipes = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            # "is_subscribed",
            # "recipes",
            # "password",
        ]
        read_only_fields = ("password",)

# class UserMeSerializer(ModelSerializer):
    

    # def get_recipes(self, user):
    #     request = self.context.get("request")
    #     return RecipeUserListsSerializer(
    #         user.recipes, many=True, context={"request": request}
    #     ).data


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(ModelSerializer):
    name = CharField(source="ingredient.name")
    measurement_unit = CharField(source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


# GET
class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_ingredient"
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            # "is_favorited",
            # "is_in_shopping_cart",
        )


class RecipeIngredientCreateSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeIngredientListSerializer(ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeListSerializer(ModelSerializer):
    ingredients = RecipeIngredientListSerializer(
        many=True, source="recipe_ingredient"
    )
    author = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class RecipeUserListsSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        read_only_fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        # read_only_fields = ("__all__",)


class RecipeCreateSerializer(ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True, write_only=True)
    author = HiddenField(default=CurrentUserDefault())
    # author = UserSerializer(read_only=True)
    image = Base64ImageField()

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

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance, context={"request": self.context.get("request")}
        ).data
