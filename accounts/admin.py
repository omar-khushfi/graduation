from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *
from accounts.models import User

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {"fields": ("is_verified",)}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ("is_verified",)}),
    )

    list_display = BaseUserAdmin.list_display + ("is_verified",)

    list_filter = BaseUserAdmin.list_filter + ("is_verified",)
admin.site.register(User,UserAdmin)

@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'reset_id', 'created_when')
