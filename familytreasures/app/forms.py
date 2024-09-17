from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth import authenticate
# from app.models import User
from django.contrib.auth import get_user_model  # get_user_modelをインポート
from .models import Children, Diary, DiaryMedia, Comment, Weather, Stamp, Template, Artwork, GrowthRecord
from .models import User
User = get_user_model()  # 動的にカスタムユーザーモデルを取得
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
            'image_url': forms.FileInput(),  # ファイル入力を使って画像をアップロード
        }


class ChildrenForm(forms.ModelForm):
    class Meta:
        model = Children
        fields = [ 'child_name', 'birthdate']  
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}),  # 日付入力用のウィジェット
        }

class InvitationSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['user_name', 'email', 'password1', 'password2'] 

class DiaryForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['child', 'template', 'stamp', 'weather', 'content', 'entry_date']

    child = forms.ModelChoiceField(
        queryset=Children.objects.none(),  # 初期値を空にしておく
        required=False,
        empty_label="子供を選択してください",
        label="子供"
    )


    weather = forms.ModelChoiceField(
        queryset=Weather.objects.all(),  # 天気のリストをプルダウンメニューに表示
        required=False,  # 選択を任意にする
        empty_label="天気を選択してください",
        label="天気"
    )
    
    stamp = forms.ModelChoiceField(
        queryset=Stamp.objects.all(),
        required=False,  # 選択を任意にする
        empty_label="気持ちを選択してください",
        label="気持ちのスタンプ",
        widget=forms.Select(attrs={'class': 'stamp-select'})  # スタンプを選択するためのフィールド
    )

    template = forms.ModelChoiceField(
        queryset=Template.objects.all(),
        required=False,  # 選択を任意にする
        empty_label="定型文を選択してください",
        label="一言"
    )
    
    entry_date = forms.DateField(
        initial=timezone.now,  # デフォルトで今日の日付を設定
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="日記の日付"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # ユーザー情報を取得
        super().__init__(*args, **kwargs)
        
        # 現在のユーザーに関連する子供のリストを表示
        if user:
            self.fields['child'].queryset = Children.objects.filter(household=user.household)
        else:
            self.fields['child'].queryset = Children.objects.none()  # デフォルトは空にする

class DiaryMediaForm(forms.ModelForm):
    class Meta:
        model = DiaryMedia
        # fields = ['media_type', 'media_url']
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
            'creation_date': forms.SelectDateWidget(years=range(2010, 2040)),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        self.fields['creation_date'].initial = timezone.now().date()  # 現在の日付をデフォルトに設定
        if user:
            self.fields['child'].queryset = Children.objects.filter(household=user.household)
            
class GrowthRecordForm(forms.ModelForm):
    class Meta:
        model = GrowthRecord
        fields = ['child', 'measurement_date', 'height', 'weight', 'memo']
        widgets = {
            'measurement_date': forms.SelectDateWidget(years=range(2010, 2040)),  # 年月日入力用のウィジェット
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)
        if user:
            # ログインユーザーに関連付けられた子供のリストをプルダウンに表示
            self.fields['child'].queryset = Children.objects.filter(household=user.household)