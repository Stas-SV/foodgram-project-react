from django.contrib import admin

from .models import Recipe, Tag, Ingredient


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'text',
        'author'
    )
    search_fields = ('id',)
    list_filter = ('name', 'author')


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
    )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)