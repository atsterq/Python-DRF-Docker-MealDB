# from rest_framework.permissions import (
#     AllowAny,
#     # IsAdminOrReadOnly,
#     IsAuthenticated,
# )
from api.permissions import Admin, AuthUser, Guest
from api.serializers import (  # UserSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    TagSerializer,
)

# from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag
from rest_framework.decorators import action

# from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

# from users.models import User


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [Admin | Guest]
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [Admin | Guest]
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    # queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

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
        if self.request.method == "GET":
            return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# class UserViewSet(ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

# @action(
#     detail=False,
#     methods=[
#         "get",
#     ],
#     permission_classes=(IsAuthenticated,),
# )
# def me(self, request):
#     user = request.user
#     serializer = UserSerializer(user, context={"request": request})
#     return Response(serializer.data)
