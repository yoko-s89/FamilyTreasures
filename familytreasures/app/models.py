from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,  AbstractBaseUser, PermissionsMixin
)
from django.conf import settings  # AUTH_USER_MODELを使用するためにsettingsをインポート
import uuid
from django.db import models
from django.utils import timezone


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

    household = models.ForeignKey('Household', on_delete=models.SET_NULL, null=True, blank=True)
    user_name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    image_url = models.ImageField(upload_to='profile_images/', null=True, blank=True)
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

class Invitation(models.Model):
    household = models.ForeignKey('Household', on_delete=models.CASCADE)  # Householdを文字列で参照
    token = models.UUIDField(default=uuid.uuid4, unique=True)  # 固有のトークンを生成
    is_used = models.BooleanField(default=False)  # 招待が使用済みかどうかを示す
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日
    updated_at = models.DateTimeField(auto_now=True)  # 更新日
    expires_at = models.DateTimeField()  # 有効期限expires_at = models.DateTimeField()  # 有効期限
    
    def is_valid(self):
        # 現在時刻が有効期限内であり、まだ使用されていないか確認
        return timezone.now() < self.expires_at  and not self.is_used 
    def __str__(self):
        return f"Invitation to {self.household} (Used: {self.is_used})"


"""子供の情報"""
class Children(models.Model):
    household = models.ForeignKey('Household', on_delete=models.CASCADE, null=True, blank=True)  # householdをオプションに
    child_name = models.CharField(max_length=255)  # こどもの名前
    birthdate = models.DateField()  # 生年月日
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日
    updated_at = models.DateTimeField(auto_now=True)  # 更新日

    def __str__(self):
        return self.child_name

    class Meta:
        db_table = 'children'  # テーブル名を明示的に指定
        



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
    child = models.ForeignKey('Children', on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey('Template', on_delete=models.SET_NULL, null=True, blank=True)
    stamp = models.ForeignKey('Stamp', on_delete=models.SET_NULL, null=True, blank=True)
    weather = models.ForeignKey('Weather', on_delete=models.SET_NULL, null=True, blank=True)  # 天気を外部キーで設定
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        child_name = self.child.child_name if self.child else "No Child"
        return f"{self.user.user_name} の日記 ({child_name} - {self.created_at.date()})"
    
    class Meta:
        db_table = 'diaries'     

class DiaryMedia(models.Model):
    """日記に関連するメディアを管理するモデル"""
    MEDIA_TYPE_CHOICES = [
        ('image', '画像'),
        ('video', '動画'),
    ]

    diary = models.ForeignKey('Diary', on_delete=models.CASCADE)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    # media_url = models.TextField()  # メディアファイルのURLやパスをtext型に変更
    media_file = models.FileField(upload_to='diary_media/')  # メディアファイルのパスを保存
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    
    def __str__(self):
        diary_name = self.diary.child.name if self.diary and self.diary.child else "No Diary"
        return f"Media for {diary_name}'s diary - {self.media_type}"
    class Meta:
        db_table = 'diary_media'     


"""コメント"""
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)# 投稿者
    diary = models.ForeignKey('Diary', on_delete=models.CASCADE)  # 日記への外部キー
    content = models.TextField()  # コメント内容
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日
    updated_at = models.DateTimeField(auto_now=True)  # 更新日

    def __str__(self):
        return f"{self.user.user_name} のコメント (日記: {self.diary.child.name})"
    
    class Meta:
        db_table = "comments"
        

class Artwork(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    child = models.ForeignKey('Children', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='artworks/')
    title = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateField()
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class GrowthRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ユーザーの外部キー
    child = models.ForeignKey('Children', on_delete=models.CASCADE)  # 子供の外部キー
    height = models.FloatField()  # 身長（cm）
    weight = models.FloatField()  # 体重（kg）
    measurement_date = models.DateField()  # 計測日
    memo = models.TextField(blank=True, null=True)  # メモ（オプション）
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日
    updated_at = models.DateTimeField(auto_now=True)  # 更新日

    def __str__(self):
        return f"{self.child.child_name} - {self.measurement_date}"

    class Meta:
        db_table = 'growth_records'  # テーブル名を指定