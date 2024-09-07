from django import forms
from django.contrib.auth.forms import UserCreationForm
from app.models import User
from django.contrib.auth import authenticate
from .models import Children, Diary, DiaryMedia


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
    
    

class ChildrenForm(forms.ModelForm):
    class Meta:
        model = Children
        fields = ['household', 'child_name', 'birthdate']  # 外部キーをフォームに含める


class DiaryForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['child', 'template', 'stamp', 'content']
        # widgets = {
        #     'content': forms.Textarea(attrs={'rows': 5}),  # 日記内容のテキストエリアを設定
        # }

    child = forms.ModelChoiceField(
        queryset=Children.objects.all(),  # 子供のリストをプルダウンメニューに表示
        empty_label="子供を選択してください",  # 初期値として表示するメッセージ
        label="子供"  # フィールドのラベル
    )

class DiaryMediaForm(forms.ModelForm):
    class Meta:
        model = DiaryMedia
        fields = ['media_type', 'media_url']
        widgets = {
            'media_url': forms.ClearableFileInput(attrs={'multiple': True}),  # 複数ファイル選択を許可
        }
