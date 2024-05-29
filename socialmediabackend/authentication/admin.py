from django.contrib import admin
from .models import User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'username', 'is_superuser', 'is_active', 'gender', 'mobile', 'status', 'profile_picture']

admin.site.register(User, UserAdmin)