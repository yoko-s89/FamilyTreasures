from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Household, Children


admin.site.register(Household)
admin.site.register(Children)

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['user_name', 'email', 'is_staff', 'is_superuser']  # 表示フィールドの指定
    search_fields = ['user_name', 'email']  # 検索対象のフィールドを指定
    ordering = ['user_name']
    
    


