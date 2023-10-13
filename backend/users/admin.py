from django.contrib import admin

from .models import User, Subscribe


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'pk',
        'email',
        'password',
        'first_name',
        'last_name',
    )
    list_editable = ('password', )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author'
    )
    list_editable = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
