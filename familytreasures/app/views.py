from app.forms import SignupForm, LoginForm, ChildrenForm, ArtworkForm, GrowthRecordForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin,  UserPassesTestMixin
from django.contrib.auth import get_user_model  # get_user_modelを使用
User = get_user_model()
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.http import HttpResponseForbidden  
from django.utils import timezone
import datetime
from dateutil.relativedelta import relativedelta
from itertools import chain
from datetime import datetime, date
from django.utils import timezone
from .forms import (ChildrenForm, DiaryForm, DiaryMediaForm, CommentForm, 
                    InvitationSignupForm,  UserProfileForm, AccountUpdateForm
)
from .models import(
    Children, Diary, DiaryMedia, Comment, Artwork, Invitation,
    Household, User, GrowthRecord
)
from uuid import UUID
# Create your views here.


class SignupView(View):
    def get(self, request):
        form = SignupForm()
        return render(request, "signup.html", context={
            "form": form
        })

    def post(self, request):
        print(request.POST)
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # 新しいhouseholdを作成し、ユーザーに関連付ける
            household = Household.objects.create()
            user.household = household
            user.save()  # householdが関連付けられた状態でユーザーを保存
            login(request, user)
            return redirect("app:home")
        return render(request, "signup.html", context={
            "form": form
        })


class InviteSignupView(View):
    template_name = 'signup_from_invitation.html'

    def get_invitation(self, token):
        # トークンが有効なUUID形式かどうかをチェック
        try:
            UUID(token, version=4)  # UUID形式かどうか確認
        except ValueError:
            # UUIDでない場合、Noneを返す
            return None
        
        # トークンで招待を検索し、有効性を検証する共通メソッド
        invitation = get_object_or_404(Invitation, token=token)
        if not invitation.is_valid() or invitation.is_used:
            return None
        return invitation

    def get(self, request, token=None):
        print(f"Token received: {token}")  # ログ出力
        # 招待トークンを検証
        invitation = self.get_invitation(token)
        if not invitation:
            print("Invitation not found or invalid.")  # ログ出力
            return render(request, 'invite_invalid.html')  # 無効な招待の場合
        form = InvitationSignupForm()
        return render(request, "signup_from_invitation.html", context={
            "form": form,
            "token": token
        })

    def post(self, request, token=None):
        form = InvitationSignupForm(request.POST)
        # 招待トークンを検証
        invitation = self.get_invitation(token)
        if not invitation:
            return render(request, 'invite_invalid.html')  # 無効な招待の場合
        
        if form.is_valid():
            user = form.save(commit=False)
            # 招待を使用済みにしてユーザーを世帯に関連付け
            invitation.is_used = True
            invitation.save()
            user.household = invitation.household
            user.save()
            messages.success(request, 'アカウントが作成されました。ログインしてください。')
            # 登録後にログイン画面へリダイレクト
            return redirect(reverse('app:login'))  # ログインページにリダイレクト

        return render(request, "signup_from_invitation.html", context={
            "form": form,
            "token": token
        })

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "login.html", {"form": form})

    def post(self, request):
        # print(request.POST)
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("app:home")
        return render(request, "login.html", {"form": form}) 
class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "home.html")

def use_invitation(request, token):
    # トークンで招待を検索
    invitation = get_object_or_404(Invitation, token=token)

    # 招待が有効であれば
    if invitation.is_valid() and not invitation.is_used:
        # 招待を使用済みにして有効期限を現在の時刻に設定
        invitation.is_used = True
        invitation.expires_at = timezone.now()
        invitation.save()

        # ここでユーザーを世帯に追加するなどの処理を実行
        request.user.household = invitation.household
        request.user.save()

        return redirect('app:home')  # 適切なリダイレクト先に変更
    else:
        # 招待が無効または既に使用されている場合のエラーページを表示
        return render(request, 'invite_invalid.html')


@login_required
def create_invitation_view(request):
    user = request.user
    
    # Householdを取得（ユーザーが所属するhousehold）
    household = user.household

    if not household:
        # 世帯がない場合、新しい世帯を作成
        household = Household.objects.create()
        user.household = household
        user.save()

    if request.method == 'POST':
        # 招待URLを作成
        expires_at = timezone.now() + datetime.timedelta(days=1)  # 有効期限を1日後に設定
        invitation = Invitation.objects.create(
            household=household,
            expires_at=expires_at
        )

        # 招待URLの作成
        invite_url = request.build_absolute_uri(f"/join/{invitation.token}/")
        context = {
            'invite_url': invite_url,
            'created': True,  # 招待が作成されたフラグ
            'message': '家族招待URLを作成しました。以下のリンクを共有してください。',
        }
        return render(request, 'create_invitation.html', context)
    
    # 初回のGETリクエスト時
    context = {
        'created': False,  # 招待がまだ作成されていない
    }
    return render(request, 'create_invitation.html', context)


@login_required
def my_page(request):
    # ユーザー情報
    user = request.user

    # 家族リスト（同じhouseholdのユーザー）
    family_members = User.objects.filter(household=user.household).exclude(id=user.id)

    # 子供のリスト
    children_list = Children.objects.filter(household=user.household)

    # ユーザープロフィールの編集
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'プロフィールが更新されました。')
            return redirect('app:my_page')
    else:
        form = UserProfileForm(instance=user)

    context = {
        'user': user,
        'form': form,
        'family_members': family_members,
        'children_list': children_list,
    }

    return render(request, 'my_page.html', context)

# family_deleteビューの追加
@login_required
def family_delete(request, id):
    # 家族メンバーを削除するロジックを実装
    member = get_object_or_404(User, id=id)
    # householdが現在のユーザーのものと一致する場合に削除を実行
    if member.household == request.user.household:
        member.household = None  # Householdから削除
        member.save()
        messages.success(request, '家族メンバーを削除しました。')
    else:
        messages.error(request, 'この操作を実行する権限がありません。')
    return redirect('app:my_page')

@login_required
def account_update(request):
    user = request.user

    if request.method == 'POST':
        form = AccountUpdateForm(request.POST, instance=user)
        if form.is_valid():
            # 現在のパスワードを確認
            current_password = form.cleaned_data['current_password']
            if not user.check_password(current_password):
                form.add_error('current_password', '現在のパスワードが正しくありません。')
            else:
                # パスワード変更を実行
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                # パスワードを変更した後にセッションを更新
                update_session_auth_hash(request, user)
                messages.success(request, 'アカウント情報が更新されました。')
                return redirect('app:login')  # ログイン画面へリダイレクト
    else:
        form = AccountUpdateForm(instance=user)

    return render(request, 'account_update.html', {'form': form})



# 子供の情報作成
class ChildrenCreateView(View):
    def get(self, request):
        # 空のフォームを生成してテンプレートに渡す
        form = ChildrenForm()
        return render(request, "children_form.html",{"form": form})

    def post(self, request):
        # POSTデータでフォームを生成
        form = ChildrenForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            
            # householdが存在する場合のみ関連付ける
            if request.user.household:
                child.household = request.user.household
            
            child.save()  # householdがなくても保存
            return redirect("app:my_page")  # 成功時にリダイレクト
        
        # フォームが無効な場合、エラーとともにフォームを再表示
        return render(request, "children_form.html", {"form": form, "errors": form.errors})    



class ChildrenUpdateDeleteView(View):
    def get(self, request, pk=None):
        # 子供のデータが存在しない場合はメッセージを表示
        if not Children.objects.exists():
            return render(request, "no_children.html")

        # 存在する場合は通常通りデータを取得
        child = get_object_or_404(Children, pk=pk)
        form = ChildrenForm(instance=child)
        return render(request, "children_form_delete.html", {
            "form": form,
            "child": child
        })

    def post(self, request, pk=None):
        # 子供のデータが存在しない場合はメッセージを表示
        if not Children.objects.exists():
            return render(request, "no_children.html")

        # 存在する場合の更新・削除処理
        child = get_object_or_404(Children, pk=pk)

        if '保存' in request.POST:  # ボタンの name 属性に合わせて条件分岐を変更
            form = ChildrenForm(request.POST, instance=child)
            if form.is_valid():
                form.save()
                # 編集後にマイページにリダイレクト
                return redirect('app:my_page')
            else:
                # フォームが無効な場合、エラーメッセージとともに表示
                return render(request, "children_form_delete.html", {
                    "form": form,
                    "child": child
                })

        elif '削除' in request.POST:  # ボタンの name 属性に合わせて条件分岐を変更
            child.delete()
            # 削除後にマイページにリダイレクト
            return redirect('app:my_page')

        # どちらの条件も満たさない場合、フォームを再表示
        form = ChildrenForm(instance=child)
        return render(request, "children_form_delete.html", {
            "form": form,
            "child": child
        })



#日記投稿画面
class DiaryCreateView(View):
    template_name = 'diary_form.html'
    success_url = 'app:diary_list'  # 投稿後にリダイレクトするURL

    def get(self, request):
        form = DiaryForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = DiaryForm(request.POST, request.FILES)
        media_files = request.FILES.getlist('media_url')  # 画像や動画のファイルを取得

        if form.is_valid():
            diary = form.save(commit=False)
            diary.user = request.user  # ログインユーザーを日記に関連付ける
            diary.save()

            # メディアファイルの保存
            for media_file in media_files:
                media = DiaryMedia(
                    diary=diary,
                    media_file=media_file,
                    media_type = 'image' if media_file.content_type.startswith('image') else 'video'
                )
                media.save()
            # 投稿後に一覧画面にリダイレクト
            return redirect(self.success_url)

        # バリデーションエラーの場合、フォームを再表示
        return render(request, self.template_name, {'form': form})
    


class DiaryListView(LoginRequiredMixin, View):
    template_name = 'diary_list.html'  # 一覧ページのテンプレート

    def get(self, request):
        selected_child = request.GET.get('child')  # プルダウンから選択された子供のIDを取得
        
        # 子供の選択用プルダウンのために子供のリストを取得
        children = Children.objects.all()

        # 日記を新しい順に取得
        if selected_child:
            # 選択された子供の日記をフィルタリング
            diaries = Diary.objects.filter(child_id=selected_child).order_by('-created_at')
        else:
            # 全ての日記を取得
            diaries = Diary.objects.all().order_by('-created_at')

        # 各日記に関連する最初の画像を取得
        for diary in diaries:
            first_image = diary.diarymedia_set.filter(media_type='image').first()
            diary.first_image = first_image  # テンプレートで使用できるように属性として設定

        return render(request, self.template_name, {
            'diaries': diaries,
            'children': children,
            'selected_child': selected_child,
        })


class DiaryDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):
        diary = get_object_or_404(Diary, pk=pk)
        comments = Comment.objects.filter(diary=diary).order_by('-created_at')
        return render(request, "diary_detail.html", context={
            "diary": diary,
            "comments": comments
        })
        

class DiaryEditView(View):
    template_name = 'diary_edit.html'  # 編集ページのテンプレート

    def get(self, request, pk):
        # 編集する日記を取得
        diary = get_object_or_404(Diary, pk=pk)
        form = DiaryForm(instance=diary)  # 既存のインスタンスをフォームに渡す
        return render(request, self.template_name, {'form': form, 'diary': diary})

    def post(self, request, pk):
        # 編集する日記を取得
        diary = get_object_or_404(Diary, pk=pk)
        form = DiaryForm(request.POST, request.FILES, instance=diary)  # インスタンスをフォームに渡す

        if form.is_valid():
            form.save()  # データベースに保存
            # 編集した日記の詳細ページにリダイレクト
            return redirect(reverse('app:diary_detail', kwargs={'pk': diary.pk}))

        # バリデーションエラーがある場合、フォームを再表示
        return render(request, self.template_name, {'form': form, 'diary': diary})

class DiaryDeleteView(View):
    template_name = 'diary_confirm_delete.html'  # 削除確認ページのテンプレート

    def get(self, request, pk):
        # 削除する日記を取得
        diary = get_object_or_404(Diary, pk=pk)
        return render(request, self.template_name, {'diary': diary})

    def post(self, request, pk):
        # 削除する日記を取得
        diary = get_object_or_404(Diary, pk=pk)
        diary.delete()  # 日記を削除
        # 削除後に一覧ページにリダイレクト
        return redirect(reverse('app:diary_list'))

class CommentCreateView(View):
    def get(self, request, diary_id):
        form = CommentForm()
        diary = get_object_or_404(Diary, pk=diary_id)
        return render(request, "comment_form.html", context={
            "form": form,
            "diary": diary
        })

    def post(self, request, diary_id):
        diary = get_object_or_404(Diary, pk=diary_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.diary = diary
            comment.save()
            return redirect('app:diary_detail', pk=diary_id)
        return render(request, "comment_form.html", context={
            "form": form,
            "diary": diary
        })

class CommentEditView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'comment_edit.html'

    def get(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        form = CommentForm(instance=comment)
        return render(request, self.template_name, {
            'form': form,
            'comment': comment
        })

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'コメントが編集されました。')
            return redirect('app:diary_detail', pk=comment.diary.pk)
        messages.error(request, 'コメントの編集に失敗しました。')
        return render(request, self.template_name, {
            'form': form,
            'comment': comment
        })

    def test_func(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        return self.request.user == comment.user
    
# app/views.py

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'comment_confirm_delete.html'

    def get(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        return render(request, self.template_name, {
            'comment': comment
        })

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        diary_pk = comment.diary.pk
        comment.delete()
        messages.success(request, 'コメントが削除されました。')
        return redirect('app:diary_detail', pk=diary_pk)

    def test_func(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        return self.request.user == comment.user

class ArtworkCreateView(LoginRequiredMixin, View):
    template_name = 'artwork_form.html'

    def get(self, request):
        # ログインしているユーザーを渡してフォームを初期化
        form = ArtworkForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        # POSTデータとユーザー情報を渡してフォームを初期化
        form = ArtworkForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.user = request.user  # ログインユーザーを作品に関連付ける
            artwork.save()
            return redirect('app:artwork_list')  # 作品一覧ページにリダイレクト
        return render(request, self.template_name, {'form': form})


class ArtworkListView(LoginRequiredMixin, View):
    template_name = 'artwork_list.html'

    
    def get(self, request):
        selected_child = request.GET.get('child')
        
        # 全ての子供のリストを取得
        children = Children.objects.filter(household=request.user.household)
        
        # 作品をフィルタリング
        if selected_child:
            # 特定の子供に絞り込み
            artworks = Artwork.objects.filter(user=request.user, child_id=selected_child)
        else:
            # 全ての投稿を表示
            artworks = Artwork.objects.filter(user=request.user)
        
        return render(request, self.template_name, {
            'artworks': artworks,
            'children': children,
            'selected_child': selected_child
        })

class ArtworkDetailView(LoginRequiredMixin, View):
    template_name = 'artwork_detail.html'

    def get(self, request, pk):
        artwork = get_object_or_404(Artwork, pk=pk, user=request.user)  # ログインユーザーの作品のみ取得
        return render(request, self.template_name, {'artwork': artwork})
    
class ArtworkEditView(LoginRequiredMixin, View):
    template_name = 'artwork_edit.html'

    def get(self, request, pk):
        artwork = get_object_or_404(Artwork, pk=pk, user=request.user)  # ログインユーザーの作品のみ取得
        form = ArtworkForm(instance=artwork, user=request.user)
        return render(request, self.template_name, {'form': form, 'artwork': artwork})

    def post(self, request, pk):
        artwork = get_object_or_404(Artwork, pk=pk, user=request.user)
        form = ArtworkForm(request.POST, request.FILES, instance=artwork, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('app:artwork_detail', pk=artwork.pk)
        return render(request, self.template_name, {'form': form, 'artwork': artwork})
    
class ArtworkDeleteView(LoginRequiredMixin, View):
    template_name = 'artwork_confirm_delete.html'

    def get(self, request, pk):
        artwork = get_object_or_404(Artwork, pk=pk, user=request.user)  # ログインユーザーの作品のみ取得
        return render(request, self.template_name, {'artwork': artwork})

    def post(self, request, pk):
        artwork = get_object_or_404(Artwork, pk=pk, user=request.user)
        artwork.delete()
        
class GrowthRecordCreateView(LoginRequiredMixin, View):
    template_name = 'growth_record_form.html'

    def get(self, request):
        form = GrowthRecordForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = GrowthRecordForm(request.POST, user=request.user)
        if form.is_valid():
            growth_record = form.save(commit=False)
            growth_record.user = request.user  # ログインユーザーを記録に関連付ける
            growth_record.save()
            return redirect('app:growth_record_list')  # 成功時に一覧画面にリダイレクト
        return render(request, self.template_name, {'form': form})
    
class GrowthRecordListView(LoginRequiredMixin, View):
    def get(self, request):
        selected_child = request.GET.get('child')
        
        # 子供のリスト
        children = Children.objects.filter(household=request.user.household)
        
        # 成長記録の取得
        if selected_child:
            growth_records = GrowthRecord.objects.filter(child_id=selected_child).order_by('-measurement_date')
        else:
            growth_records = GrowthRecord.objects.all().order_by('-measurement_date')
        
        # 年齢の計算
        for record in growth_records:
            age = relativedelta(record.measurement_date, record.child.birthdate)
            record.age_years = age.years
            record.age_months = age.months

        return render(request, 'growth_record_list.html', {
            'growth_records': growth_records,
            'children': children,
            'selected_child': selected_child,
        })



class GrowthRecordUpdateView(LoginRequiredMixin, View):
    template_name = 'growth_record_update.html'

    def get(self, request, pk):
        # 編集対象の成長記録を取得
        record = get_object_or_404(GrowthRecord, pk=pk)
        form = GrowthRecordForm(instance=record)
        return render(request, self.template_name, {'form': form, 'record': record})

    def post(self, request, pk):
        # 編集対象の成長記録を取得
        record = get_object_or_404(GrowthRecord, pk=pk)
        form = GrowthRecordForm(request.POST, instance=record)

        # 「保存」ボタンが押された場合
        if 'save' in request.POST and form.is_valid():
            form.save()
            # 成功時に詳細画面にリダイレクト
            return redirect('app:growth_record_list')

        # 「削除」ボタンが押された場合
        elif 'delete' in request.POST:
            record.delete()
            # 削除後に一覧画面にリダイレクト
            return redirect('app:growth_record_list')

        # バリデーションエラーがある場合、フォームを再表示
        return render(request, self.template_name, {'form': form, 'record': record})
    
    
class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        def ensure_datetime(dt):
            
            if isinstance(dt, date):
                dt = datetime.combine(dt, datetime.min.time())
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            return dt
        
        diaries = [
            {
                'created_at': ensure_datetime(d.created_at),
                'id': d.id,
                'type': 'diary',
                'content': d.content,  # 日記の内容
                'template': d.template.text if d.template else '',  # 一言
                'first_image': d.diarymedia_set.filter(media_type='image').first().media_file.url if d.diarymedia_set.filter(media_type='image').exists() else None,
                'detail_url': reverse('app:diary_detail', args=[d.id]),  # 日記の詳細ページへのリンク
            }
            for d in Diary.objects.all()
        ]
        artworks = [
            {
                'created_at': ensure_datetime(a.created_at),
                'id': a.id,
                'type': 'artwork',
                'child_name': a.child.child_name,
                'title': a.title,  # 作品名
                'image': a.image.url if a.image else None,  # 添付画像
                'detail_url': reverse('app:artwork_detail', args=[a.id]),  # 制作物の詳細ページへのリンク
            }
            for a in Artwork.objects.all()
        ]

        
        growth_records = [
            {
                'created_at': ensure_datetime(g.measurement_date),
                'id': g.id,
                'type': 'growth_record',
                'child_name': g.child.child_name,
                'height': g.height,
                'weight': g.weight,
                'memo': g.memo,
                'list_url': reverse('app:growth_record_list'),  # 成長記録の一覧ページへのリンク
            }
            for g in GrowthRecord.objects.all()
        ]

        combined_list = sorted(
            chain(diaries, artworks, growth_records),
            key=lambda x: x['created_at'],
            reverse=True
        )

        return render(request, "home.html", context={
            "combined_list": combined_list
        })
