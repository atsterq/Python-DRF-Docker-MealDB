from api.filters import IngredientFilter, RecipeFilter
from api.permissions import Admin, AuthUser, Guest
from api.serializers import (
    CustomUserSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    RecipeSerializer,
    TagSerializer,
    UserSubscriptionSerializer,
)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscription, User


class TagViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    Viewset for list and retrieve tags.

    Admins can add and edit tags.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [Admin | Guest]
    pagination_class = None
    http_method_names = ["get"]


class IngredientViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    Viewset for list and retrieve ingredients.

    Admins can add and edit ingredients.

    Users can search ingredients by name.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [Admin | Guest]
    pagination_class = None
    http_method_names = ["get"]
    filter_backends = (IngredientFilter,)
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Viewset for recipes.

    Authorized users can add new recipes.
    All users can browse recipes.
    Admins can add and edit recipes.

    Users can filter recipes by author, tags,
    if it in shopping cart or favorited.
    """

    permission_classes = [Admin | AuthUser | Guest]
    http_method_names = ["get", "post", "delete", "patch"]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        """
        Method for getting queryset.
        """
        recipes = Recipe.objects.prefetch_related(
            "recipe_ingredient__ingredient", "tags"
        ).all()
        return recipes

    def get_serializer_class(self):
        """
        Method for serializer class.
        """
        if self.request.method == "POST" or self.request.method == "PATCH":
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """
        Method for creating a recipe.
        """
        serializer.save(author=self.request.user)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        url_path="favorite",
        permission_classes=[Admin | AuthUser],
    )
    def post_delete_favorite(self, request, pk):
        """
        Method for adding or deleting recipe from favorited.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            Favorite.objects.get_or_create(
                user=self.request.user, recipe=recipe
            )
            serializer = RecipeListSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = get_object_or_404(
            Favorite, user=self.request.user, recipe=recipe
        )
        favorite.delete()
        response = Response(
            "status: Deleted from favorite.",
            status=status.HTTP_204_NO_CONTENT,
        )
        return response

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        url_path="shopping_cart",
        permission_classes=[Admin | AuthUser],
    )
    def post_delete_shopping_cart(self, request, pk):
        """
        Method for adding or deleting recipe from shopping cart.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            ShoppingCart.objects.get_or_create(
                user=self.request.user, recipe=recipe
            )
            serializer = RecipeListSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        shopping_cart = get_object_or_404(
            ShoppingCart, user=self.request.user, recipe=recipe
        )
        shopping_cart.delete()
        response = Response(
            "status: Deleted from shopping cart.",
            status=status.HTTP_204_NO_CONTENT,
        )
        return response

    @action(
        methods=["GET"],
        detail=False,
        url_path="download_shopping_cart",
        permission_classes=[Admin | AuthUser],
    )
    def download_shopping_cart(self, request):
        """
        Method for downloading a shopping list file.
        """
        if not request.user.shopping_cart.exists():
            return Response(
                "error: Shopping cart is empty.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        ingredient_list = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )

        shopping_cart_list = []
        shopping_cart_list.append("   Shopping list:")
        for ingredient in ingredient_list:
            shopping_cart_list.append(
                (
                    f'•  {ingredient.get("ingredient__name")} '
                    f'({ingredient.get("ingredient__measurement_unit")}) '
                    f'— {ingredient.get("amount")}'
                )
            )
        response = HttpResponse(
            content="\n".join(shopping_cart_list),
            content_type="text/plain; charset=UTF-8",
        )
        response[
            "Content-Disposition"
        ] = "attachment; filename=shopping-list.txt"
        return response


class CustomUserViewSet(UserViewSet):
    """
    Viewset for users.

    Registration, authorization, listing users.

    Users can subscribe, unsubscribe and browse their subscriptions.
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [Admin | AuthUser | Guest]
    http_method_names = ["get", "post", "delete"]

    @action(
        methods=["GET"],
        detail=False,
        url_path="subscriptions",
        permission_classes=[Admin | AuthUser],
    )
    def get_subscriptions(self, request):
        """
        Method for get user subscriptions.
        """
        queryset = User.objects.filter(author__user=request.user)
        if not queryset.exists():
            return Response(
                "status: You don't have subscriptions.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        pages = self.paginate_queryset(queryset)
        serializer = UserSubscriptionSerializer(
            pages, many=True, context={"request": request}
        )
        response = self.get_paginated_response(serializer.data)
        return response

    @action(
        methods=["POST", "DELETE"],
        detail=False,
        url_path=r"(?P<pk>\d+)/subscribe",
        permission_classes=[Admin | AuthUser],
    )
    def post_delete_subscription(self, request, pk):
        """
        Method for subscribe and unsubscribe to authors.
        """
        user = get_object_or_404(User, username=request.user)
        author = get_object_or_404(User, pk=pk)
        if self.request.method == "POST":
            Subscription.objects.get_or_create(user=user, author=author)
            serializer = UserSubscriptionSerializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = get_object_or_404(
            Subscription, user=user, author=author
        )
        subscription.delete()
        response = Response(
            "status: Unsubscribed.",
            status=status.HTTP_204_NO_CONTENT,
        )
        return response
