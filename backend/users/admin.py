from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_display_links = ('id', 'username', 'email')
    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    ordering = ('username',)
