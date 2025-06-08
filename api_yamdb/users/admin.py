from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'first_name',
        'last_name',
        'is_staff',
    )
    list_editable = ('role',)
    fieldsets = BaseUserAdmin.fieldsets
    search_fields = ('username', 'email', 'first_name', 'last_name')
