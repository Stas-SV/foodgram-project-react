from django.contrib import admin

from .models import Recipe, Tag, Ingredient, RecipeIngredient, Favorite, ShoppingList


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name'
    )
    search_fields = ('id',)
    list_filter = ('name', 'author', 'tags')


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color'
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'amount'
    )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user'
    )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
