import base64

from django.core.files.base import ContentFile
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from rest_framework import serializers
from users.models import Subscription, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]
        read_only_fields = ("password",)

    def get_is_subscribed(self, data):
        if not self.context:
            return False
        username = self.context["request"].user
        if not username.is_authenticated or data.username == username:
            return False
        user = get_object_or_404(User, username=username)
        author = get_object_or_404(User, username=data.username)
        return Subscription.objects.filter(user=user, author=author).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        ]


class UserSubscriptionSerializer(CustomUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, user):
        request = self.context.get("request")
        return RecipeListSerializer(
            user.recipes, many=True, context={"request": request}
        ).data

    def get_is_subscribed(self, data):
        if not self.context:
            return False
        username = self.context["request"].user
        if not username.is_authenticated or data.username == username:
            return False
        user = get_object_or_404(User, username=username)
        author = get_object_or_404(User, username=data.username)
        return Subscription.objects.filter(user=user, author=author).exists()

    def get_recipes_count(self, data):
        author = get_object_or_404(User, username=data.username)
        return Recipe.objects.filter(author=author).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
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


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


# class RecipeUserListsSerializer(ModelSerializer):
#     class Meta:
#         model = Recipe
#         fields = (
#             "id",
#             "name",
#             "image",
#             "cooking_time",
#         )
#         read_only_fields = (
#             "id",
#             "name",
#             "image",
#             "cooking_time",
#         )
# read_only_fields = ("__all__",)
class RecipeIngredientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeCreateListSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientListSerializer(
        many=True, source="recipe_ingredient"
    )
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

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


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True, write_only=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
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
            # "is_favorited",
            # "is_in_shopping_cart",
        )

    # def get_is_favorited(self, instance):
    #     pass

    # def get_is_in_shopping_cart(self, instance):
    #     pass

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
        return RecipeCreateListSerializer(
            instance, context={"request": self.context.get("request")}
        ).data

    # def validate_ingredients(self, instance):
    #     if not instance:
    #         raise ValidationError("At least one ingredient should be added.")

    #     ingredients_list = []
    #     for item in instance:
    #         ingredient = get_object_or_404(Ingredient, id=item.get('id'))
    #         if ingredient in ingredients_list:
    #             raise ValidationError("Ingredients can't be duplicated.")
    #         if int(item["amount"]) <= 0:
    #             raise ValidationError(
    #                 "Ingredient amount should be more than 0."
    #             )
    #         ingredients_list.append(ingredient)
    #     return instance

    # def validate_tags(self, instance):
    #     if not instance:
    #         raise ValidationError("At least one tag should be added.")

    #     # tag_list = []
    #     # for item in instance:
    #     #     tag = get_object_or_404(Tag, id=item["id"])
    #     #     if tag in tag_list:
    #     #         raise ValidationError("Tags can't be duplicated.")
    #     #     tag_list.append(tag)
    #     return instance


class FavoriteSerializer(RecipeListSerializer):
    class Meta:
        model = Favorite
        fields = ("user", "recipe")

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class ShoppingCartSerializer(RecipeListSerializer):
    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance, context={"request": self.context.get("request")}
        ).data

    # def to_representation(self, instance):
    #     return representation(
    #         self.context, instance.recipe, RecipeShortSerializer
    #     )
