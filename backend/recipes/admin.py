from django.contrib import admin

from .models import Recipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'text',
        'author'
    )
    search_fields = ('id',)
    list_filter = ('name', 'author')


admin.site.register(Recipe, RecipeAdmin)
