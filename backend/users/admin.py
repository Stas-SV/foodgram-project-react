from django.contrib import admin

from .models import User


# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'email',
        'username',
        'first_name',
        'last_name'
    )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
