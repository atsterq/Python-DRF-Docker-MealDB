from api.views import CustomUserViewSet, index

# ; IngredientViewSet,; RecipeViewSet,; TagViewSet,
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)

urlpatterns = [
    path("index", index),
    path("auth/", include("djoser.urls.authtoken")),
    path('', include(router.urls))
]
