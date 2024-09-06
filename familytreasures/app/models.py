from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,  AbstractBaseUser, PermissionsMixin
)

# Create your models here.


class UserManager(BaseUserManager):

    def create_user(self, user_name, email, password=None):
        if not email:
            raise ValueError('メールアドレスを入力してください')
        
        if self.model.objects.filter(email=self.normalize_email(email)).exists():
            raise ValueError('指定されたメールアドレスは既に使用されています')
        user = self.model(
            user_name=user_name,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_name, email, password=None):
        user = self.create_user(
            user_name=user_name,
            email=email,
            password=password
        )
        user.set_password(password)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    # first_name = None
    # last_name = None
    # date_joined = None
    # username = None
    # groups = None
    # user_permissions = None

    user_name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    image_url = models.CharField(max_length=300,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    # last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "user_name" #このテーブルのレコードを一意に識別
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]#スーパーユーザー作成時に使用

    objects = UserManager()
    
    def __str__(self):
        return self.user_name

    class Meta:
        db_table = "users"
        
        
"""世帯"""
class Household(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時（レコード作成時に自動で設定）
    updated_at = models.DateTimeField(auto_now=True)  # 更新日時（レコードが更新されるたびに自動で設定）

    class Meta:
        db_table = 'households'  # テーブル名を指定
        
"""子供の情報"""
class Children(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE)  # 外部キーとして定義
    child_name = models.CharField(max_length=255)  # こどもの名前
    birthdate = models.DateField()  # 生年月日
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日
    updated_at = models.DateTimeField(auto_now=True)  # 更新日

    def __str__(self):
        return self.child_name

    class Meta:
        db_table = 'children'  # テーブル名を明示的に指定
        
