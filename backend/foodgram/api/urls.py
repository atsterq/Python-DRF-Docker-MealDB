from api.views import CustomUserViewSet, RecipeViewSet, TagViewSet, index

# IngredientViewSet, RecipeViewSet,
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register("users", CustomUserViewSet)
router.register("tags", TagViewSet)
router.register("recipes", RecipeViewSet)

urlpatterns = [
    path("index", index),
    path("auth/", include("djoser.urls.authtoken")),
    path("", include(router.urls)),
]
