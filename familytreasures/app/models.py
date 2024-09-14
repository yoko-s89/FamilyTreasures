from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,  AbstractBaseUser, PermissionsMixin
)
# from django.contrib.auth.models import User
from django.conf import settings  # AUTH_USER_MODELを使用するためにsettingsをインポート





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
        


class Child(models.Model):
    """子供の情報を管理するモデル"""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Template(models.Model):
    """定型文を管理するモデル"""
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text[:50]  # 定型文の最初の50文字を表示
    class Meta:
        db_table = 'templates' 

class Stamp(models.Model):
    """気持ちスタンプを管理するモデル"""
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='stamps/')  # 画像ファイルを保存するフィールド
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'stamps' 
        
class Weather(models.Model):
    """天気を管理するモデル"""
    name = models.CharField(max_length=50)  # 天気の名前
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'weather'  # テーブル名を指定

class Diary(models.Model):
    """日記を管理するモデル"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # settings.AUTH_USER_MODELを使用
    # child = models.ForeignKey(Child, on_delete=models.CASCADE, null=True, blank=True)
    child = models.ForeignKey(Child, on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True)
    stamp = models.ForeignKey(Stamp, on_delete=models.SET_NULL, null=True, blank=True)
    weather = models.ForeignKey('Weather', on_delete=models.SET_NULL, null=True, blank=True)  # 天気を外部キーで設定
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        child_name = self.child.name if self.child else "No Child"
        return f"{self.user.user_name} の日記 ({child_name} - {self.created_at.date()})"
    
    # def __str__(self):
    #     return f"{self.user.user_name} の日記 ({self.child.name if self.child else '子供なし'} - {self.created_at.date()})"
    class Meta:
        db_table = 'diaries'     

class DiaryMedia(models.Model):
    """日記に関連するメディアを管理するモデル"""
    MEDIA_TYPE_CHOICES = [
        ('image', '画像'),
        ('video', '動画'),
    ]

    diary = models.ForeignKey(Diary, on_delete=models.CASCADE)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    # media_url = models.TextField()  # メディアファイルのURLやパスをtext型に変更
    media_file = models.FileField(upload_to='diary_media/')  # メディアファイルのパスを保存
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     diary_name = self.diary.child.name if self.diary and self.diary.child else "No Diary"
    #     return f"Media for {self.diary.child.name}'s diary - {self.media_type}"
    
    def __str__(self):
        diary_name = self.diary.child.name if self.diary and self.diary.child else "No Diary"
        return f"Media for {diary_name}'s diary - {self.media_type}"
    class Meta:
        db_table = 'diary_media'     


"""コメント"""
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)# 投稿者
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE)  # 日記への外部キー
    content = models.TextField()  # コメント内容
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日
    updated_at = models.DateTimeField(auto_now=True)  # 更新日

    def __str__(self):
        return f"{self.user.user_name} のコメント (日記: {self.diary.child.name})"
    
    class Meta:
        db_table = "comments"