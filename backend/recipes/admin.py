from django.contrib import admin

from .models import Recipe, Tag, Ingredient


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
        'measurements'
    )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)