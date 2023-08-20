import base64

from django.core.files.base import ContentFile
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
    """
    Serializer for recipes image.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    """
    Serializer for user model.
    """

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
        """
        Method for checking if current user is subscribed to viewed author.
        """
        if not self.context:
            return False
        subscription = Subscription.objects.filter(
            user=self.context.get("request").user.id, author=data
        )
        return subscription.exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Serializer for creating new users.
    """

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
    """
    Serializer for users subscriptions.
    """

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

    def get_recipes(self, data):
        """
        Method for getting user's recipes.
        """
        request = self.context.get("request")
        serializer = RecipeListSerializer(
            data.recipes, many=True, context={"request": request}
        )
        return serializer.data

    def get_is_subscribed(self, data):
        """
        Method for checking if current user is subscribed to viewed author.
        """
        if not self.context:
            return False
        subscription = Subscription.objects.filter(
            user=self.context.get("request").user.id, author=data
        )
        return subscription.exists()

    def get_recipes_count(self, data):
        """
        Method for counting user's recipes.
        """
        recipes = Recipe.objects.filter(author=data)
        return recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for tags.
    """

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for ingredients.
    """

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing a recipe.
    """

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        read_only_fields = ("__all__",)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for nested ingredient field in listed recipe.
    """

    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for nested ingredient field in created recipe.
    """

    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for listing a recipe.
    """

    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipe_ingredient"
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

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
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, data):
        """
        Method for checking if recipe is favorited by current user.
        """
        favorited = Favorite.objects.filter(
            user=self.context.get("request").user.id, recipe=data
        )
        return favorited.exists()

    def get_is_in_shopping_cart(self, data):
        """
        Method for checking if recipe is in user's shopping cart.
        """
        shopping_cart = ShoppingCart.objects.filter(
            user=self.context.get("request").user.id, recipe=data
        )
        return shopping_cart.exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating a recipe.
    """

    ingredients = RecipeIngredientCreateSerializer(many=True, write_only=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
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
        """
        Method for creating a recipe.
        """
        ingredients = validated_data.pop("ingredients")
        instance = super().create(validated_data)
        for ingredient_data in ingredients:
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient_data["ingredient"],
                amount=ingredient_data["amount"],
            ).save()
        return instance

    def update(self, instance, validated_data):
        """
        Method for updating a recipe.
        """
        ingredients = validated_data.pop("ingredients")
        instance = super().update(instance, validated_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient_data in ingredients:
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient_data["ingredient"],
                amount=ingredient_data["amount"],
            ).save()
        return instance

    def to_representation(self, instance):
        """
        Method for representing a recipe.
        """
        serializer = RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        )
        return serializer.data
