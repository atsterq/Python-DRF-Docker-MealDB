from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    CustomUserViewSet,
    TagViewSet,
)
from django.urls import include, path, re_path
from rest_framework import routers

router = routers.DefaultRouter()
router.register("users", CustomUserViewSet, basename="subscriptions")
router.register("tags", TagViewSet, basename="tags")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("ingredients", IngredientViewSet, basename="ingredients")


urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
]
