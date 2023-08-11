from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionUserViewSet,
    TagViewSet,
)
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register("users", SubscriptionUserViewSet, basename="subscriptions")
router.register("tags", TagViewSet, basename="tags")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("ingredients", IngredientViewSet, basename="ingredients")


urlpatterns = [
    path("", include("djoser.urls")),
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
