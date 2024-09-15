from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Household, Children, Diary, Template, Stamp, DiaryMedia, Weather

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # ユーザー一覧ページで表示するフィールド
    list_display = ['user_name', 'email', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['user_name', 'email']
    ordering = ['user_name']
    
    # フィールドセットのカスタマイズ
    fieldsets = (
        (None, {'fields': ('user_name', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Personal Info', {'fields': ('image_url', 'household')}),
    )
    
    # ユーザー作成ページで表示するフィールド
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_name', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

# その他のモデルを登録
admin.site.register(Household)
admin.site.register(Children)
admin.site.register(Diary)
admin.site.register(Template)
admin.site.register(Stamp)
admin.site.register(DiaryMedia)

@admin.register(Weather)
class WeatherAdmin(admin.ModelAdmin):
    list_display = ['name']





# from django.contrib import admin
# from django.contrib.auth import get_user_model
# from django.contrib.auth.admin import UserAdmin
# from .models import Household, Children, Diary, Template, Stamp, DiaryMedia, Weather



# admin.site.register(Household)
# admin.site.register(Children)
# admin.site.register(Diary)
# admin.site.register(Template)
# admin.site.register(Stamp)
# admin.site.register(DiaryMedia)

# User = get_user_model()

# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     list_display = ['user_name', 'email', 'is_staff', 'is_superuser']  # 表示フィールドの指定
#     search_fields = ['user_name', 'email']  # 検索対象のフィールドを指定
#     ordering = ['user_name']
    
# @admin.register(Weather)
# class WeatherAdmin(admin.ModelAdmin):
#     list_display = ['name']  # 管理画面で表示するフィールドの指定