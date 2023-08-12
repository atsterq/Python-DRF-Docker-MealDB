from api.permissions import Admin, AuthUser, Guest
from api.serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    # RecipeListSerializer,
    RecipeSerializer,
    TagSerializer,
    UserSubscriptionSerializer,
)
from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import mixins, status, viewsets
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


class IngredientViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [Admin | Guest]
    pagination_class = None


# `create()`, `retrieve()`, `update()`,
#     `partial_update()`, `destroy()` and `list()` actions.
class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [Admin | AuthUser | Guest]
    http_method_names = ['get', 'post', 'delete', 'patch']

    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)

        # from django.db import connection  # trap
        # print(len(connection.queries))
        # for q in connection.queries:
        #     print(">>>>", q["sql"])

        return res

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            "recipe_ingredient__ingredient", "tags"
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RecipeCreateSerializer
        # if self.request.method == "GET":
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SubscriptionUserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [Admin | AuthUser]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        if self.request.method == "GET":
            return Subscription.objects.all()
        user = get_object_or_404(User, username=self.request.user)
        subscription = Subscription.objects.filter(user=user).values("author")
        return User.objects.filter(pk__in=subscription)

    # @action(
    #     methods=["get"],
    #     detail=False,
    #     url_path="/subscriptions",
    # )
    # def subscription_get(self, request, pk=None):
    #     user = get_object_or_404(User, username=request.user)
    #     # author = get_object_or_404(User, pk=pk)
    #     subscriptions = Subscription.objects.get(user=user)
    #     subscriptions_serializer =
    #     return subscriptions_serializer

    @action(
        methods=["post", "delete"],
        detail=False,
        url_path=r"(?P<pk>\d+)/subscribe",
    )
    def subscription_post_delete(self, request, pk=None):
        user = get_object_or_404(User, username=request.user)
        author = get_object_or_404(User, pk=pk)
        if self.request.method == "POST":
            Subscription.objects.get_or_create(user=user, author=author)
            subscription_serializer = UserSubscriptionSerializer(author)
            return Response(
                subscription_serializer.data, status=status.HTTP_201_CREATED
            )
        subscription = get_object_or_404(
            Subscription, user=user, author=author
        )
        subscription.delete()
        return Response(
            {"detail": "Unsubscribed."}, status=status.HTTP_204_NO_CONTENT
        )
