from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,  AbstractBaseUser, PermissionsMixin
)
from django.conf import settings 
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
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    image_url = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"Household {self.id}"

    class Meta:
        db_table = 'households'

# class Household(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True) 
#     updated_at = models.DateTimeField(auto_now=True) 

#     class Meta:
#         db_table = 'households'  

class Invitation(models.Model):
    household = models.ForeignKey('Household', on_delete=models.CASCADE)  
    token = models.UUIDField(default=uuid.uuid4, unique=True)  # 固有のトークンを生成
    is_used = models.BooleanField(default=False)  # 招待が使用済みかどうかを示す
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  
    expires_at = models.DateTimeField()  # 有効期限
    
    def is_valid(self):
        # 現在時刻が有効期限内であり、まだ使用されていないか確認
        return timezone.now() < self.expires_at  and not self.is_used 
    def __str__(self):
        return f"Invitation to {self.household} (Used: {self.is_used})"


"""子供の情報"""
class Children(models.Model):
    household = models.ForeignKey('Household', on_delete=models.CASCADE, null=True, blank=True)  
    child_name = models.CharField(max_length=255)  
    birthdate = models.DateField()  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.child_name

    class Meta:
        db_table = 'children'  
        



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
    image = models.ImageField(upload_to='stamps/')  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'stamps' 
        
class Weather(models.Model):
    """天気を管理するモデル"""
    name = models.CharField(max_length=50)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'weather'  

class Diary(models.Model):
    """日記を管理するモデル"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    household = models.ForeignKey('Household', on_delete=models.CASCADE)  
    child = models.ForeignKey('Children', on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey('Template', on_delete=models.SET_NULL, null=True, blank=True)
    stamp = models.ForeignKey('Stamp', on_delete=models.SET_NULL, null=True, blank=True)
    weather = models.ForeignKey('Weather', on_delete=models.SET_NULL, null=True, blank=True)  
    content = models.TextField(blank=True, null=True)
    entry_date = models.DateField(default=timezone.now)
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

    diary = models.ForeignKey('Diary', related_name='medias', on_delete=models.CASCADE)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    media_file = models.FileField(upload_to='diary_media/')  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        if self.media_file:
            self.media_file.delete(save=False)
        super().delete(*args, **kwargs)
    
    def __str__(self):
        diary_name = self.diary.child.name if self.diary and self.diary.child else "No Diary"
        return f"Media for {diary_name}'s diary - {self.media_type}"
    class Meta:
        db_table = 'diary_media'     


"""コメント"""
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    diary = models.ForeignKey('Diary', on_delete=models.CASCADE)  
    content = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        diary_name = self.diary.child.child_name if self.diary and self.diary.child else "No Diary"
        return f"{self.user.user_name} のコメント (日記: {diary_name})"
    
    class Meta:
        db_table = "comments"
        

class Artwork(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    child = models.ForeignKey('Children', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='artworks/')
    title = models.CharField(max_length=100)
    comment = models.TextField()
    creation_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  
    
    def __str__(self):
        return self.title
    
class GrowthRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    child = models.ForeignKey('Children', on_delete=models.CASCADE)  
    height = models.FloatField()  # 身長（cm）
    weight = models.FloatField()  # 体重（kg）
    measurement_date = models.DateField(default=timezone.now)  # 計測日
    memo = models.TextField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"{self.child.child_name} - {self.measurement_date}"

    class Meta:
        db_table = 'growth_records'  