import base64

from django.core.files.base import ContentFile
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
        username = self.context["request"].user
        if not username.is_authenticated or data.username == username:
            return False
        user = get_object_or_404(User, username=username)
        author = get_object_or_404(User, username=data.username)
        return Subscription.objects.filter(user=user, author=author).exists()


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

    def get_recipes(self, user):
        """
        Method for user's recipes.
        """
        request = self.context.get("request")
        return RecipeListSerializer(
            user.recipes, many=True, context={"request": request}
        ).data

    def get_is_subscribed(self, data):
        """
        Method for checking if current user is subscribed to viewed author.
        """
        if not self.context:
            return False
        username = self.context["request"].user
        if not username.is_authenticated or data.username == username:
            return False
        user = get_object_or_404(User, username=username)
        author = get_object_or_404(User, username=data.username)
        return Subscription.objects.filter(user=user, author=author).exists()

    def get_recipes_count(self, data):
        """
        Method for counting user's recipes.
        """
        author = get_object_or_404(User, username=data.username)
        return Recipe.objects.filter(author=author).count()


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


class RecipeIngredientListSerializer(serializers.ModelSerializer):
    """
    Serializer for nested ingredient field.
    """

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeCreateListSerializer(serializers.ModelSerializer):
    """
    Serializer for representation a created recipe.
    """

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

    def get_is_favorited(self, instance):
        """
        Method for checking if recipe is favorited by current user.
        """
        favorited = Favorite.objects.filter(
            user=self.context.get("request").user.id, recipe=instance
        )
        return favorited.exists()

    def get_is_in_shopping_cart(self, instance):
        """
        Method for checking if recipe is in user's shopping cart.
        """
        shopping_cart = ShoppingCart.objects.filter(
            user=self.context.get("request").user.id, recipe=instance
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
        return RecipeCreateListSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class FavoriteSerializer(RecipeListSerializer):
    """
    Serializer for users favorite recipes.
    """

    class Meta:
        model = Favorite
        fields = ("user", "recipe")

    def to_representation(self, instance):
        """
        Method for representing a favorite recipe.
        """
        return RecipeListSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class ShoppingCartSerializer(RecipeListSerializer):
    """
    Serializer for shopping cart.
    """

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")
