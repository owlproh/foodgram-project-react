from django.contrib import admin
from foodgram.settings import LIST_PER_PAGE

from .models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'password',
        'first_name',
        'last_name',
        'email',
        'is_stuff',
    )
    empty_value_display = '<--пусто-->'
    list_editable = ('is_stuff',)
    list_filter = ('username', 'email',)
    search_fields = ('username', 'email',)
    list_per_page = LIST_PER_PAGE


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'follower',
    )
    empty_value_display = '<--пусто-->'
    list_filter = ('author', 'follower',)
    search_fields = ('author', 'follower',)
    list_per_page = LIST_PER_PAGE


admin.site.site_title = 'Admin-zone of Foodgram'
admin.site.site_header = 'Admin-zone of Foodgram'
