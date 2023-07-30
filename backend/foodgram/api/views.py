from django.shortcuts import HttpResponse, render
from djoser.views import UserViewSet


def index(request):
    return HttpResponse("index")


class CustomUserViewSet(UserViewSet):
    pass
