# # serializers
# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     id = serializers.ReadOnlyField(source="ingredient.id")
#     name = serializers.CharField(source="ingredient.name")
#     measurement_unit = serializers.CharField(
#         source="ingredient.measurement_unit"
#     )

#     class Meta:
#         model = RecipeIngredient
#         fields = ("id", "name", "measurement_unit", "amount")


# class RecipeSerializer(serializers.ModelSerializer):
#     tags = TagSerializer(many=True)
#     ingredients = RecipeIngredientSerializer(
#         many=True, source="recipe_ingredient"
#     )

#     class Meta:
#         model = Recipe
#         fields = "__all__"


# class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(
#         source="ingredient", queryset=Ingredient.objects.all()
#     )

#     class Meta:
#         model = RecipeIngredient
#         fields = ("id", "amount")


# class RecipeCreateSerializer(serializers.ModelSerializer):
#     ingredients = RecipeIngredientCreateSerializer(many=True)

#     class Meta:
#         model = Recipe
#         fields = ("name", "cooking_time", "text", "tags", "ingredients")

#     def create(self, validated_data):
#         print(validated_data)
#         ingredients = validated_data.pop('ingredients')
#         return super().create(validated_data)
