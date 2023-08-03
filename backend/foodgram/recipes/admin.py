from django.contrib import admin
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    inlines = (RecipeIngredientInLine, )
    list_filter = ('name', 'author', 'tags')
# На админ-странице рецепта отображается общее число добавлений этого рецепта в избранное.


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
