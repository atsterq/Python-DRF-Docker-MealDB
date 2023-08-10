from django.contrib import admin
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription, User


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(User)
class User(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
    )
    search_fields = ("username",)
    list_filter = ("username", "email")


@admin.register(Subscription)
class Subscription(admin.ModelAdmin):
    list_display = (
        "user",
        "author",
    )
    search_fields = (
        "user",
        "author",
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    def favorite(self, obj):
        return obj.favorite.count()

    list_display = ("name", "author", "favorite")
    inlines = (RecipeIngredientInLine,)
    list_filter = ("name", "author", "tags")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    list_filter = ("name",)
    list_display = ("name", "measurement_unit")
    list_filter = ("name",)
