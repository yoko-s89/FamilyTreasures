from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Household, Children, Child, Diary, Template, Stamp, DiaryMedia



admin.site.register(Household)
admin.site.register(Children)
admin.site.register(Child)
admin.site.register(Diary)
admin.site.register(Template)
admin.site.register(Stamp)
admin.site.register(DiaryMedia)

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['user_name', 'email', 'is_staff', 'is_superuser']  # 表示フィールドの指定
    search_fields = ['user_name', 'email']  # 検索対象のフィールドを指定
    ordering = ['user_name']
    
    