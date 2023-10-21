from django.contrib import admin

from users import models

admin.site.register(models.User)


@admin.register(models.Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author', 'date_subscriptions')
