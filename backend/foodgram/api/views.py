from api.serializers import RecipeSerializer, TagSerializer
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
