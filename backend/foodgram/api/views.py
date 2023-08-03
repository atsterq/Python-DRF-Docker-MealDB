from api.serializers import (
    RecipeCreateSerializer,
    RecipeSerializer,
    TagSerializer,
)
from django.shortcuts import HttpResponse
from djoser.views import UserViewSet
from recipes.models import Recipe, Tag
from rest_framework.viewsets import ModelViewSet


def index(request):
    return HttpResponse("index")


class CustomUserViewSet(UserViewSet):
    pass


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)

        from django.db import connection

        print(len(connection.queries))
        for q in connection.queries:
            print(">>>>", q["sql"])

        return res

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            "recipe_ingredient__ingredient", "tags"
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.action == "create":  # add update
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
