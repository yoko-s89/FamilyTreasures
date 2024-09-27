from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model  
from .models import Children, Diary, DiaryMedia, Comment, Weather, Stamp, Template, Artwork, GrowthRecord, Invitation
from .models import User
User = get_user_model() 
from django.utils import timezone


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["user_name", "email", "password1", "password2"]
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("このメールアドレスは既に登録されています")
        return email

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    def clean(self):
        print("ログインフォームのクリーンが呼び出された")
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get("password")
        print(email, password)
        if email is None:
            raise forms.ValidationError("emailは必須です")
        if password is None:
            raise forms.ValidationError("passwordは必須です")
        self.user = authenticate(email=email, password=password)
        if self.user is None:
            raise forms.ValidationError("認証に失敗しました")
        return self.cleaned_data
    
    def get_user(self):
        return self.user
    
class AccountUpdateForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput, label="現在のパスワード")
    new_password = forms.CharField(widget=forms.PasswordInput, label="新しいパスワード")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="新しいパスワード（確認）")

    class Meta:
        model = User
        fields = ['user_name', 'email']
        labels = {
            'user_name': '名前/ニックネーム',
            'email': 'メールアドレス',
        }

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', 'パスワードが一致しません。')

        return cleaned_data    
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['user_name', 'image_url']  
        widgets = {
            'image_url': forms.FileInput(),  
            'user_name': forms.TextInput(attrs={'placeholder': 'ユーザ名'}),
        }

    def clean_user_name(self):
        user_name = self.cleaned_data.get('user_name')
        if User.objects.filter(user_name=user_name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("このユーザ名は既に使用されています。")
        return user_name
    

# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['user_name', 'image_url']  
#         widgets = {
#             'image_url': forms.FileInput(),  
#         }

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = User  
        fields = ['image_url']  

class ChildrenForm(forms.ModelForm):
    class Meta:
        model = Children
        fields = [ 'child_name', 'birthdate']
        labels = {
            'child_name': '名前/ニックネーム',   
            'birthdate': '誕生日',          
        }  
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}), 
        }

class InvitationSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    token = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ['user_name', 'email', 'password1', 'password2', 'token']
        labels = {
            'user_name': '名前/ニックネーム',
            'email': 'メールアドレス',
        }

    def clean_token(self):
        token = self.cleaned_data.get('token')
        if not self.validate_token(token):
            raise forms.ValidationError("無効なトークンです。")
        return token

    def validate_token(self, token):
        from uuid import UUID
        try:
            UUID(token, version=4)
        except ValueError:
            return False
        try:
            invitation = Invitation.objects.get(token=token)
            if not invitation.is_valid() or invitation.is_used:
                return False
        except Invitation.DoesNotExist:
            return False
        return True

# class InvitationSignupForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ['user_name', 'email', 'password1', 'password2'] 
#         labels = {
#             'user_name': '名前/ニックネーム',
#             'email': 'メールアドレス',
#         }

class DiaryForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['child', 'template', 'stamp', 'weather', 'content', 'entry_date']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': '内容',
                'rows': 5,
            }),
        }

    child = forms.ModelChoiceField(
        queryset=Children.objects.none(),  
        required=False,
        empty_label="子供を選択してください",
        label="子供"
    )

    # メディアの追加用フィールド
    media_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    weather = forms.ModelChoiceField(
        queryset=Weather.objects.all(),
        required=False,
        empty_label="天気を選択してください",
        label="天気"
    )
    
    stamp = forms.ModelChoiceField(
        queryset=Stamp.objects.all(),
        required=False,
        empty_label="気持ちを選択してください",
        label="気持ちのスタンプ",
        widget=forms.Select(attrs={'class': 'stamp-select'})
    )

    template = forms.ModelChoiceField(
        queryset=Template.objects.all(),
        required=False,
        empty_label="定型文を選択してください",
        label="一言"
    )
    
    entry_date = forms.DateField(
        initial=timezone.now,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="日記の日付"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DiaryForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['child'].queryset = Children.objects.filter(household=user.household)
class DiaryMediaForm(forms.ModelForm):
    class Meta:
        model = DiaryMedia
        fields = ['media_file']
        widgets = {
            'media_file': forms.ClearableFileInput(attrs={'multiple': True}),  # 複数ファイル選択を許可
        }


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 6, 
            'cols': 60,
            'placeholder': 'コメント入力',
        }),
        label='コメント内容',
        help_text='コメントを入力してください。',
        max_length=500  
    )
    class Meta:
        model = Comment
        fields = ['content']

class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ['child', 'image', 'title', 'comment', 'creation_date']
        widgets = {
            'creation_date': forms.DateInput(attrs={'type': 'date'}),
        }

    creation_date = forms.DateField(
        initial=timezone.now().date(),
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="作品の作成日"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ArtworkForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['creation_date'].initial = timezone.now().date()
        if user:
            self.fields['child'].queryset = Children.objects.filter(household=user.household)
        
# class ArtworkForm(forms.ModelForm):
#     class Meta:
#         model = Artwork
#         fields = ['child', 'image', 'title', 'comment', 'creation_date']
#         widgets = {
#             'creation_date': forms.SelectDateWidget(years=range(2010, 2040)),
#         }

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)  
#         super().__init__(*args, **kwargs)
#         self.fields['creation_date'].initial = timezone.now().date() 
#         if user:
#             self.fields['child'].queryset = Children.objects.filter(household=user.household)

class GrowthRecordForm(forms.ModelForm):
    class Meta:
        model = GrowthRecord
        fields = ['child', 'measurement_date', 'height', 'weight', 'memo']
        widgets = {
            'measurement_date': forms.DateInput(attrs={'type': 'date'}),
            'memo': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'child': '子供',
            'measurement_date': '計測日',
            'height': '身長 (cm)',
            'weight': '体重 (kg)',
            'memo': 'メモ',
        }
        help_texts = {
            'memo': 'その他のメモや詳細を記入してください。',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # ユーザー情報を取得
        super(GrowthRecordForm, self).__init__(*args, **kwargs)
        
        # 初期値として本日の日付を設定（新規作成時のみ）
        if not self.instance.pk:
            self.fields['measurement_date'].initial = timezone.now().date()
        
        # ユーザーの世帯に属する子供のみを選択可能にする
        if user:
            self.fields['child'].queryset = Children.objects.filter(household=user.household)
            
# class GrowthRecordForm(forms.ModelForm):
#     class Meta:
#         model = GrowthRecord
#         fields = ['child', 'measurement_date', 'height', 'weight', 'memo']
#         widgets = {
#             'measurement_date': forms.SelectDateWidget(years=range(2010, 2040)),  # 年月日入力用のウィジェット
#         }

#         labels = {
#             'child': '子供の名前',
#             'measurement_date': '計測日',
#             'height': '身長 (cm)',
#             'weight': '体重 (kg)',
#             'memo': 'メモ',
#         }
#         help_texts = {
#             'memo': 'その他のメモや詳細を記入してください。',
#         }


#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)  
#         super().__init__(*args, **kwargs)
#         if user:
#             self.fields['child'].queryset = Children.objects.filter(household=user.household)