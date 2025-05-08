from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from accounts.models import User


admin.site.register(User,UserAdmin)

@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'reset_id', 'created_when')
