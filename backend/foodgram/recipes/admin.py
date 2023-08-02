from django.contrib import admin
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInLine, )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass
