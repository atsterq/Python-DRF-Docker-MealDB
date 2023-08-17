from api.filters import RecipeFilter
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
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscription, User


class TagViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [Admin | Guest]
    pagination_class = None
    http_method_names = ["get"]


class IngredientViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [Admin | Guest]
    pagination_class = None
    http_method_names = ["get"]
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [Admin | AuthUser | Guest]
    http_method_names = ["get", "post", "delete", "patch"]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            "recipe_ingredient__ingredient", "tags"
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.request.method == "POST" or self.request.method == "PATCH":
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        url_path="favorite",
    )
    def favorite(self, request, pk):
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
        return Response(
            "status: Deleted from favorite.",
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        url_path="shopping_cart",
    )
    def shopping_cart(self, request, pk):
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
        return Response(
            "status: Deleted from shopping cart.",
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        methods=["GET"],
        detail=False,
        url_path="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
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
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [Admin | AuthUser | Guest]
    http_method_names = ["get", "post", "delete"]

    @action(
        methods=["GET"],
        detail=False,
        url_path="subscriptions",
    )
    def subscriptions_get(self, request):
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
        return self.get_paginated_response(serializer.data)

    @action(
        methods=["POST", "DELETE"],
        detail=False,
        url_path=r"(?P<pk>\d+)/subscribe",
    )
    def subscription_post_delete(self, request, pk):
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
        return Response(
            "status: Unsubscribed.",
            status=status.HTTP_204_NO_CONTENT,
        )
