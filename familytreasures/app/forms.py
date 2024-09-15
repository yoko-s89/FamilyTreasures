from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth import authenticate
# from app.models import User
from django.contrib.auth import get_user_model  # get_user_modelをインポート
from .models import Children, Diary, DiaryMedia, Comment, Weather, Stamp, Template, Artwork, GrowthRecord
from .models import User
User = get_user_model()  # 動的にカスタムユーザーモデルを取得


# class SignupForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ["user_name", "email", "password1", "password2"]

# from django.contrib.auth import authenticate
# from .models import Children, Diary, DiaryMedia, Comment, Weather, Stamp, Template


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
        fields = ['user_name', 'image_url']  # 必要なフィールドを指定
        widgets = {
            'image_url': forms.FileInput(),  # ファイル入力を使って画像をアップロード
        }


class ChildrenForm(forms.ModelForm):
    class Meta:
        model = Children
        fields = [ 'child_name', 'birthdate']  # 外部キーをフォームに含める
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}),  # 日付入力用のウィジェット
        }

class InvitationSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['user_name', 'email', 'password1', 'password2']  # フォームフィールドの定義


class DiaryForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['child', 'template', 'stamp', 'weather', 'content']
        # widgets = {
        #     'content': forms.Textarea(attrs={'rows': 5}),  # 日記内容のテキストエリアを設定
        # }

    child = forms.ModelChoiceField(
        queryset=Children.objects.all(),  # 子供のリストをプルダウンメニューに表示
        required=False,  # 子供の選択を任意にする
        empty_label="子供を選択してください",  # 初期値として表示するメッセージ
        label="子供"  # フィールドのラベル
    )

    weather = forms.ModelChoiceField(
        queryset=Weather.objects.all(),  # 天気のリストをプルダウンメニューに表示
        empty_label="天気を選択してください",
        label="天気"
    )
    
    stamp = forms.ModelChoiceField(
        queryset=Stamp.objects.all(),
        empty_label="気持ちを選択してください",
        label="気持ちのスタンプ",
        widget=forms.Select(attrs={'class': 'stamp-select'})  # スタンプを選択するためのフィールド
    )

    template = forms.ModelChoiceField(
        queryset=Template.objects.all(),
        empty_label="定型文を選択してください",
        label="一言"
    )
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
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        label='コメント内容',
        help_text='コメントを入力してください。',
        max_length=500  # 最大500文字
    )
    class Meta:
        model = Comment
        fields = ['content']
        
class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ['child', 'image', 'title', 'comment', 'created_at']
        widgets = {
            'created_at': forms.SelectDateWidget(years=range(2000, 2030)),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # ユーザー情報を受け取る
        super().__init__(*args, **kwargs)
        if user:
            # ログインユーザーに関連付けられた子供のリストをプルダウンに表示
            # 既存のChildrenFormと合わせるために、householdでフィルタリング
            self.fields['child'].queryset = Children.objects.filter(household=user.household)
            
class GrowthRecordForm(forms.ModelForm):
    class Meta:
        model = GrowthRecord
        fields = ['child', 'measurement_date', 'height', 'weight', 'memo']
        widgets = {
            'measurement_date': forms.SelectDateWidget(years=range(2000, 2030)),  # 年月日入力用のウィジェット
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # ユーザー情報を取得
        super().__init__(*args, **kwargs)
        if user:
            # ログインユーザーに関連付けられた子供のリストをプルダウンに表示
            self.fields['child'].queryset = Children.objects.filter(household=user.household)