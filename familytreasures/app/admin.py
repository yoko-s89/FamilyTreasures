from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Household, Children, Diary, Template, Stamp, DiaryMedia, Weather

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # ユーザー一覧ページ
    list_display = ['user_name', 'email', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['user_name', 'email']
    ordering = ['user_name']
    
    
    fieldsets = (
        (None, {'fields': ('user_name', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Personal Info', {'fields': ('image_url', 'household')}),
    )
    
    # ユーザー作成
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_name', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

# その他のモデル
admin.site.register(Household)
admin.site.register(Children)
admin.site.register(Diary)
admin.site.register(Template)
admin.site.register(Stamp)
admin.site.register(DiaryMedia)

@admin.register(Weather)
class WeatherAdmin(admin.ModelAdmin):
    list_display = ['name']




