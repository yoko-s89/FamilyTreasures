from app.forms import SignupForm, LoginForm, ChildrenForm, ArtworkForm, GrowthRecordForm, ImageUploadForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.views import PasswordChangeDoneView
from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin,  UserPassesTestMixin
from django.contrib.auth import get_user_model   
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
User = get_user_model()
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.utils import timezone
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from itertools import chain
from datetime import datetime, date
from .forms import (ChildrenForm, DiaryForm, DiaryMediaForm, CommentForm, 
                    InvitationSignupForm,  UserProfileForm, AccountUpdateForm,
                    ImageUploadForm
)
from .models import(
    Children, Diary, DiaryMedia, Comment, Artwork, Invitation,
    Household, User, GrowthRecord
)
from uuid import UUID
# Create your views here.
from collections import defaultdict
from django.http import Http404 
import logging
logger = logging.getLogger(__name__)



class PortfolioView(TemplateView):
    template_name = 'portfolio.html'

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
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("app:home")
        return render(request, "signup.html", context={
            "form": form
        })


class InviteSignupView(View):
    template_name = 'signup_from_invitation.html'

    def get_invitation(self, token):
        # トークンが有効なUUID形式かどうかをチェック
        try:
            uuid_obj = UUID(token, version=4)  # UUID形式かどうか確認
        except ValueError:
            print(f"Invalid UUID format: {token}")
            return None
        
        # トークンで招待を検索し、有効性を検証
        try:
            invitation = Invitation.objects.get(token=token)
            if not invitation.is_valid() or invitation.is_used:
                print(f"Invalid or used invitation: {token}")
                return None
            return invitation
        except Invitation.DoesNotExist:
            print(f"Invitation does not exist for token: {token}")
            return None

    def get(self, request, token=None):
        print(f"Token received: {token}")  # トークンが受け取られているかログ
        # 招待トークンを検証
        invitation = self.get_invitation(token)
        
        if not invitation:
            print(f"Invitation not found or invalid for token: {token}")  # ログ
            return render(request, 'invite_invalid.html')  # 無効な招待の場合
        
        # 既にログインしている場合
        if request.user.is_authenticated:
            if invitation.household:
                print(f"User {request.user} is already authenticated and joining household: {invitation.household}")
                request.user.household = invitation.household
                request.user.save()
                messages.success(request, '家族に参加しました。')
                return redirect('app:home')
            else:
                print("Invitation household does not exist")
                messages.error(request, '招待された世帯が存在しません。')
                return render(request, 'invite_invalid.html')

        # サインアップフォームの初期化
        form = InvitationSignupForm(initial={'token': token})
        return render(request, self.template_name, context={
            "form": form,
            "token": token
        })

    def post(self, request, token=None):
        # 招待トークンを検証
        invitation = self.get_invitation(token)
        if not invitation:
            messages.error(request, '無効な招待です。')
            print(f"Invitation not found or invalid for token: {token}")  # ログ
            return render(request, 'invite_invalid.html')  # 無効な招待の場合

        # 既にログインしている場合
        if request.user.is_authenticated:
            if invitation.household:
                request.user.household = invitation.household
                request.user.save()
                messages.success(request, '家族に参加しました。')
                return redirect('app:home')
            else:
                messages.error(request, '招待された世帯が存在しません。')
                return render(request, 'invite_invalid.html')

        # 招待を使って新規ユーザーを作成
        form = InvitationSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # 招待を使用済みにしてユーザーを世帯に関連付け
            invitation.is_used = True
            invitation.save()
            user.household = invitation.household
            user.save()

            # ユーザーを自動的にログイン
            # auth_login(request, user)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'アカウントが作成され、ログインしました。')
            return redirect("app:home")
        
        # フォームにエラーがある場合は再表示
        return render(request, self.template_name, context={
            "form": form,
            "token": token
        })

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "login.html", {"form": form})

    def post(self, request):
        # フォームに request を渡す
        form = LoginForm(request.POST, request=request)  # requestを渡す
        if form.is_valid():
            user = form.get_user()
            
            # 認証されたユーザーに対して backend がない場合、設定する
            if not hasattr(user, 'backend'):
                user.backend = 'django.contrib.auth.backends.ModelBackend'  # デフォルトのバックエンド、必要に応じて変更
                
            # ログイン処理
            login(request, user)
            return redirect("app:home")
        return render(request, "login.html", {"form": form})

# class LoginView(View):
#     def get(self, request):
#         form = LoginForm()
#         return render(request, "login.html", {"form": form})

#     def post(self, request):
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             login(request, form.get_user())
#             return redirect("app:home")
#         return render(request, "login.html", {"form": form}) 
    
class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "home.html")

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
        expires_at = timezone.now() + timedelta(days=1)  # 有効期限を1日後に設定
        invitation = Invitation.objects.create(
            household=household,
            expires_at=expires_at
        )

        # 招待URLの作成
        # invite_url = request.build_absolute_uri(f"/join/{invitation.token}/")
        # invite_url = request.build_absolute_uri(reverse('signup_from_invitation', args=[invitation.token]))
        invite_url = request.build_absolute_uri(reverse('app:signup_from_invitation', kwargs={'token': invitation.token}))
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
    user = request.user
    family_members = User.objects.filter(household=user.household).exclude(id=user.id)
    children_list = Children.objects.filter(household=user.household)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save()
            print(f"Updated user_name: {user.user_name}")  # デバッグ用
            messages.success(request, 'プロフィールが更新されました。')
            return redirect('app:my_page')
        else:
            logger.debug(f"Form errors: {form.errors}")  # デバッグ用
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
    # 家族メンバーを取得
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
def family_delete_confirm(request, id):
    # 家族メンバーを取得
    member = get_object_or_404(User, id=id)

    # 権限の確認: householdが現在のユーザーのものと一致するか確認
    if member.household != request.user.household:
        messages.error(request, 'この操作を実行する権限がありません。')
        return redirect('app:my_page')

    if request.method == 'POST':
        # 削除を実行
        member.household = None  # Householdから削除
        member.save()
        messages.success(request, '家族メンバーを削除しました。')
        return redirect('app:my_page')

    # GETリクエストの場合は確認ページを表示
    return render(request, 'family_delete_confirm.html', {'member': member})


@login_required
def account_update(request):
    user = request.user

    if request.method == 'POST':
        form = AccountUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'アカウント情報が更新されました。')
            return redirect('app:home')  # 適切なリダイレクト先に変更
    else:
        form = AccountUpdateForm(instance=user)

    return render(request, 'account_update.html', {'form': form})

# @login_required
# def account_update(request):
#     user = request.user

#     if request.method == 'POST':
#         form = AccountUpdateForm(request.POST, instance=user)
#         if form.is_valid():
#             form.save()  # ユーザー名とメールアドレスを保存
#             messages.success(request, 'アカウント情報が更新されました。')
#             return redirect('app:home')  # 適切なリダイレクト先に変更
#     else:
#         form = AccountUpdateForm(instance=user)

#     return render(request, 'account_update.html', {'form': form})


def image_update(request):
    # 現在のユーザーを取得
    user = request.user

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('app:my_page')  # アップロード後にマイページへ
    else:
        form = ImageUploadForm(instance=user)

    return render(request, 'app/image_update.html', {'form': form})

def image_delete(request):
    # 現在のユーザーを取得
    user = request.user

    if request.method == 'POST':
        # ユーザーの画像を削除
        user.image_url.delete()  # 画像ファイルを削除
        user.image_url = None
        user.save()
        return redirect('app:my_page')  # 削除後にマイページへ

    return render(request, 'app/image_delete_confirm.html')

# @login_required
# def password_change(request):
#     if request.method == 'POST':
#         form = PasswordChangeForm(user=request.user, data=request.POST)
#         if form.is_valid():
#             form.save()
#             update_session_auth_hash(request, form.user)  # ユーザーをログアウトさせない
#             messages.success(request, 'パスワードが変更されました。')
#             return redirect('password_change_done')  # カスタム完了ページにリダイレクト
#     else:
#         form = PasswordChangeForm(user=request.user)
    
#     return render(request, 'password_change.html', {'form': form})

@login_required
def custom_password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # ユーザーをログアウトさせない
            messages.success(request, 'パスワードが正常に変更されました。')
            return redirect(reverse('app:password_change_done'))  # reverse でリダイレクト
        else:
            messages.error(request, 'パスワードの変更に失敗しました。正しい情報を入力してください。')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'password_change.html', {'form': form})


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'account/password_change_done.html'  # テンプレートファイルをカスタマイズする場合
# @login_required
# def password_change_done(request):
#     return render(request, 'password_change_done.html')


# @login_required
# def password_change(request):
#     if request.method == 'POST':
#         form = PasswordChangeForm(user=request.user, data=request.POST)
#         if form.is_valid():
#             form.save()  # パスワードを保存
#             messages.success(request, 'パスワードが変更されました。')
#             return redirect('app:password_change_done')  # パスワード変更後のリダイレクト先
#     else:
#         form = PasswordChangeForm(user=request.user)

#     return render(request, 'password_change.html', {'form': form})

# @login_required
# def password_change_done(request):
#     return render(request, 'password_change_done.html')


# 子供の情報作成


class ChildrenCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ChildrenForm()
        return render(request, "children_form.html",{"form": form})

    def post(self, request):
        form = ChildrenForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            
            # householdが存在する場合のみ関連付ける
            if request.user.household:
                child.household = request.user.household
            
            child.save()  # householdがなくても保存
            return redirect("app:my_page")  # 成功時にリダイレクト
        
        return render(request, "children_form.html", {"form": form, "errors": form.errors})    


class ChildrenUpdateDeleteView(LoginRequiredMixin, View):
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

        if '保存' in request.POST:  
            form = ChildrenForm(request.POST, instance=child)
            if form.is_valid():
                form.save()
                # 編集後にマイページへ
                return redirect('app:my_page')
            else:
                # フォームが無効な場合、エラーメッセージとともに表示
                return render(request, "children_form_delete.html", {
                    "form": form,
                    "child": child
                })

        elif '削除' in request.POST:  
            child.delete()
            # 削除後にマイページへ
            return redirect('app:my_page')

        # どちらの条件も満たさない場合、フォームを再表示
        form = ChildrenForm(instance=child)
        return render(request, "children_form_delete.html", {
            "form": form,
            "child": child
        })



#日記投稿画面
class DiaryCreateView(LoginRequiredMixin, View):
    template_name = 'diary_form.html'
    success_url = reverse_lazy('app:diary_list')
    
    def get(self, request):
        form = DiaryForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = DiaryForm(user=request.user, data=request.POST, files=request.FILES)  
        # media_files = request.FILES.getlist('media_url')  
        media_files = request.FILES.getlist('media_files')  # フィールド名を 'media_files' に修正

        if form.is_valid():
            diary = form.save(commit=False)
            diary.user = request.user
            diary.household = request.user.household  
            diary.save()

            # メディアファイルの保存
            for media_file in media_files:
                media = DiaryMedia(
                    diary=diary,
                    media_file=media_file,
                    media_type = 'image' if media_file.content_type.startswith('image') else 'video'
                )
                media.save()
            # 投稿後に一覧画面へ
            return redirect(self.success_url)

        # バリデーションエラーの場合、フォームを再表示
        return render(request, self.template_name, {'form': form})
    
class DiaryListView(LoginRequiredMixin, View):
    template_name = 'diary_list.html'

    def get(self, request):
        selected_filter = request.GET.get('child')

        # 子供の選択用プルダウンのために、家族の子供リストを取得
        children = Children.objects.filter(household=request.user.household)

        # 家族のみの投稿を取得するための基本クエリ
        diaries = Diary.objects.filter(user__household=request.user.household).order_by('-entry_date')

        # 特定のフィルタに応じて日記を絞り込み
        if selected_filter == 'none':
            # 特定の子供が設定されていない日記（家族日記）を取得
            diaries = diaries.filter(child=None)
        elif selected_filter and selected_filter != 'all':
            # 特定の子供に絞り込む
            child = get_object_or_404(Children, id=selected_filter, household=request.user.household)
            diaries = diaries.filter(child=child)

        # 各日記に関連する最初の画像を取得
        for diary in diaries:
            diary.first_image = diary.medias.filter(media_type='image').first()

        # 日記を西暦ごとにグループ化
        grouped_diaries = defaultdict(list)
        for diary in diaries:
            grouped_diaries[diary.entry_date.year].append(diary)

        grouped_diaries = sorted(grouped_diaries.items(), key=lambda x: x[0], reverse=True)

        return render(request, self.template_name, {
            'grouped_diaries': grouped_diaries,
            'children': children,
            'selected_filter': selected_filter,
        })    

class DiaryDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        # pkとhouseholdを考慮して日記を取得
        diary = Diary.objects.filter(
            Q(pk=pk) & (Q(child__household=request.user.household) | Q(child=None, user__household=request.user.household))
        ).first()

        # 日記が存在しない場合は404エラーを発生させる
        if not diary:
            raise Http404("Diary not found")

        # コメントを取得
        comments = Comment.objects.filter(diary=diary).order_by('-created_at')
        
        # テンプレートに渡すコンテキスト
        return render(request, "diary_detail.html", context={
            "diary": diary,
            "comments": comments
        })

class DiaryEditView(LoginRequiredMixin, View):
    template_name = 'diary_edit.html'

    def get(self, request, pk):
        # 日記を取得（childがある場合とない場合の両方を考慮）
        diary = get_object_or_404(
            Diary,
            Q(user__household=request.user.household) &
            (Q(child__isnull=True) | Q(child__household=request.user.household)),
            pk=pk
        )
        
        # フォームの初期化
        form = DiaryForm(instance=diary, user=request.user)
        
        # 日記に関連するメディアの取得
        media_list = diary.medias.all()

        return render(request, self.template_name, {
            'form': form,
            'diary': diary,
            'media_list': media_list
        })

    def post(self, request, pk):
        # 日記を取得（childがある場合とない場合の両方を考慮）
        diary = get_object_or_404(
            Diary,
            Q(user__household=request.user.household) &
            (Q(child__isnull=True) | Q(child__household=request.user.household)),
            pk=pk
        )

        # フォームのインスタンスを作成（FILES を除外）
        form = DiaryForm(request.POST, instance=diary, user=request.user)

        # アップロードされた複数ファイルを取得
        media_files = request.FILES.getlist('media_files')

        if form.is_valid():
            # 日記の保存
            form.save()
            logger.debug(f"Diary ID {diary.pk} saved successfully.")

            # ファイルのバリデーション
            for media_file in media_files:
                if media_file.size > 5 * 1024 * 1024:  # 5MB 制限
                    form.add_error(None, "各ファイルは5MB以下でなければなりません。")
                    logger.error(f"File {media_file.name} exceeds 5MB.")
                    return render(request, self.template_name, {
                        'form': form,
                        'diary': diary,
                        'media_list': diary.medias.all(),
                        'errors': form.errors
                    })
                if not media_file.content_type.startswith('image/') and not media_file.content_type.startswith('video/'):
                    form.add_error(None, "画像または動画ファイルのみアップロード可能です。")
                    logger.error(f"File {media_file.name} has invalid content type {media_file.content_type}.")
                    return render(request, self.template_name, {
                        'form': form,
                        'diary': diary,
                        'media_list': diary.medias.all(),
                        'errors': form.errors
                    })

            # 新しいメディアの追加
            for media_file in media_files:
                media_type = 'image' if media_file.content_type.startswith('image/') else 'video'
                DiaryMedia.objects.create(
                    diary=diary,
                    media_file=media_file,
                    media_type=media_type
                )
                logger.debug(f"Added {media_type} media to Diary ID {diary.pk}.")

            # 削除対象のメディアIDを取得
            delete_media_ids = request.POST.getlist('delete_media')
            if delete_media_ids:
                deleted_count, _ = DiaryMedia.objects.filter(id__in=delete_media_ids, diary=diary).delete()
                logger.debug(f"Deleted {deleted_count} media items from Diary ID {diary.pk}.")

            # 編集後、詳細ページにリダイレクト
            return redirect(reverse('app:diary_detail', kwargs={'pk': diary.pk}))
        else:
            # バリデーションエラー時の処理
            logger.error(f"Diary form is invalid for Diary ID {diary.pk}: {form.errors}")
            media_list = diary.medias.all()
            return render(request, self.template_name, {
                'form': form,
                'diary': diary,
                'media_list': media_list,
                'errors': form.errors  # エラーメッセージをテンプレートに渡す
            })
# class DiaryEditView(LoginRequiredMixin, View):
    # template_name = 'diary_edit.html'

    # def get(self, request, pk):
    #     # 日記を取得
    #     try:
    #         diary = Diary.objects.get(pk=pk)
    #     except Diary.DoesNotExist:
    #         raise Http404("Diary not found")

    #     # 家族のみが編集できるように制限
    #     if diary.user.household != request.user.household:
    #         raise PermissionDenied("この日記を編集する権限がありません。")

    #     form = DiaryForm(instance=diary, user=request.user)
    #     media_list = diary.medias.all()  # 日記に関連するメディアを取得

    #     return render(request, self.template_name, {
    #         'form': form,
    #         'diary': diary,
    #         'media_list': media_list
    #     })

    # def post(self, request, pk):
    #     # 日記を取得
    #     try:
    #         diary = Diary.objects.get(pk=pk)
    #     except Diary.DoesNotExist:
    #         raise Http404("Diary not found")

    #     # 家族のみが編集できるように制限
    #     if diary.user.household != request.user.household:
    #         raise PermissionDenied("この日記を編集する権限がありません。")

    #     form = DiaryForm(request.POST, request.FILES, instance=diary, user=request.user)

    #     if form.is_valid():
    #         form.save()

    #         # 新しいメディアを追加
    #         media_files = request.FILES.getlist('media_files')
    #         for media_file in media_files:
    #             media_type = 'image' if media_file.content_type.startswith('image') else 'video'
    #             DiaryMedia.objects.create(diary=diary, media_file=media_file, media_type=media_type)

    #         # 削除するメディアのIDを取得
    #         delete_media_ids = request.POST.getlist('delete_media')

    #         if delete_media_ids:
    #             DiaryMedia.objects.filter(id__in=delete_media_ids, diary=diary).delete()

    #         # 編集後、詳細ページにリダイレクト
    #         return redirect(reverse('app:diary_detail', kwargs={'pk': diary.pk}))
    #     else:
    #         # バリデーション失敗時にメディアリストを再取得
    #         media_list = diary.medias.all()
    #         return render(request, self.template_name, {
    #             'form': form,
    #             'diary': diary,
    #             'media_list': media_list,
    #             'errors': form.errors  # エラーメッセージをテンプレートに渡す
    #         })        
        

    # def post(self, request, pk):
    #     # childがNoneの場合も考慮して日記を取得
    #     if Diary.objects.filter(pk=pk, child__isnull=False).exists():
    #         diary = get_object_or_404(Diary, pk=pk, child__household=request.user.household)
    #     else:
    #         diary = get_object_or_404(Diary, pk=pk, child=None)

    #     form = DiaryForm(request.POST, request.FILES, instance=diary, user=request.user)

    #     print("POST request data:", request.POST)
    #     print("FILES request data:", request.FILES)

    #     if form.is_valid():
    #         print("Form is valid.")  # フォームが有効ならデバッグ出力

    #         form.save()

    #         # 新しいメディアを追加
    #         media_files = request.FILES.getlist('media_files')
    #         for media_file in media_files:
    #             media_type = 'image' if media_file.content_type.startswith('image') else 'video'
    #             DiaryMedia.objects.create(diary=diary, media_file=media_file, media_type=media_type)

    #         # 削除するメディアのIDを取得
    #         delete_media_ids = request.POST.getlist('delete_media')
    #         print("Delete media IDs:", delete_media_ids)  # 削除対象のメディアIDをデバッグ出力

    #         if delete_media_ids:
    #             DiaryMedia.objects.filter(id__in=delete_media_ids, diary=diary).delete()
    #             print("Deleted media with IDs:", delete_media_ids)  # 削除完了の確認

    #         # 編集後、詳細ページにリダイレクト
    #         return redirect(reverse('app:diary_detail', kwargs={'pk': diary.pk}))
    #     else:
    #         print("Form is invalid.")  # フォームが無効ならデバッグ出力
    #         print(form.errors)  # エラーメッセージを出力

    #     # バリデーション失敗時にメディアリストを再取得
    #     media_list = diary.medias.all()
    #     return render(request, self.template_name, {
    #         'form': form,
    #         'diary': diary,
    #         'media_list': media_list,
    #         'errors': form.errors  # エラーメッセージをテンプレートに渡す
    #     })
        
class DiaryDeleteView(LoginRequiredMixin, View):
    template_name = 'diary_confirm_delete.html'  

    def get(self, request, pk):
        # childがNoneの場合も考慮して、削除する日記を取得
        # diary = get_object_or_404(Diary, pk=pk, child__household=request.user.household) if Diary.objects.filter(pk=pk, child__isnull=False).exists() else get_object_or_404(Diary, pk=pk, child=None)
        diary = get_object_or_404(Diary, pk=pk, user__household=request.user.household)  # 家族のみに制限
        return render(request, self.template_name, {'diary': diary})

    def post(self, request, pk):
        # 日記を取得し、家族に基づいてアクセス制御
        diary = get_object_or_404(Diary, pk=pk, user__household=request.user.household)
        diary.delete()  # 日記を削除
        # 削除後に一覧ページへリダイレクト
        return redirect(reverse('app:diary_list'))
    
    # def post(self, request, pk):
    #     # childがNoneの場合も考慮して、削除する日記を取得
    #     diary = get_object_or_404(Diary, pk=pk, child__household=request.user.household) if Diary.objects.filter(pk=pk, child__isnull=False).exists() else get_object_or_404(Diary, pk=pk, child=None)
    #     diary.delete()  # 日記を削除
    #     # 削除後に一覧ページへ
    #     return redirect(reverse('app:diary_list'))


class DeleteMediaView(LoginRequiredMixin, View):
    def post(self, request, pk, media_pk):
        media = DiaryMedia.objects.filter(
            Q(diary__child__household=request.user.household) | Q(diary__child=None, diary__user__household=request.user.household),
            pk=media_pk,
            diary__pk=pk
        ).first()

        # メディアが存在しない場合は404エラー
        if not media:
            raise Http404("Media not found")

        # メディアの削除処理
        media.delete()

        # 削除後、日記の編集ページへリダイレクト
        return redirect(reverse('app:diary_edit', kwargs={'pk': pk}))

# class DeleteMediaView(LoginRequiredMixin, View):
#     def post(self, request, pk, media_pk):
#         # Qオブジェクトを最初に使い、フィルタを作成
#         media = DiaryMedia.objects.filter(
#             Q(diary__child__household=request.user.household) | Q(diary__child=None, diary__user__household=request.user.household),
#             pk=media_pk,
#             diary__pk=pk
#         ).first()

#         # メディアが存在しない場合は404エラー
#         if not media:
#             raise Http404("Media not found")

#         # メディアの削除処理
#         media.delete()

#         # 削除後、日記の編集ページへリダイレクト
#         return redirect(reverse('app:diary_edit', kwargs={'pk': pk}))
    
    # def post(self, request, pk, media_pk):
    #     # メディアの削除処理
    #     media = get_object_or_404(DiaryMedia, pk=media_pk, diary__pk=pk)
    #     media.delete()
    #     # 削除後、編集ページへ
    #     return redirect(reverse('app:diary_edit', kwargs={'pk': pk}))
class CommentCreateView(LoginRequiredMixin, View):
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
        form = ArtworkForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.user = request.user
            artwork.household = request.user.household  
            artwork.save()
            return redirect('app:artwork_list')  # 作品一覧ページへ
        else:
            return render(request, self.template_name, {'form': form})


class ArtworkListView(LoginRequiredMixin, View):
    template_name = 'artwork_list.html'

    def get(self, request):
        selected_child = request.GET.get('child')

        # 全ての子供のリストを取得（ログインユーザーの家族に属する子供）
        children = Children.objects.filter(household=request.user.household)

        # 作品をフィルタリング
        if selected_child:
            try:
                # 特定の子供に絞り込み
                selected_child = int(selected_child)  
                artworks = Artwork.objects.filter(child_id=selected_child, user__household=request.user.household).order_by('-creation_date')
            except ValueError:
                # フィルタが無効な場合、すべての作品を表示
                artworks = Artwork.objects.filter(user__household=request.user.household).order_by('-creation_date')
        else:
            # 同じ家族の全ての作品を表示
            artworks = Artwork.objects.filter(user__household=request.user.household).order_by('-creation_date')

        return render(request, self.template_name, {
            'artworks': artworks,
            'children': children,
            'selected_child': selected_child
        })

class ArtworkDetailView(LoginRequiredMixin, View):
    template_name = 'artwork_detail.html'

    def get(self, request, pk):
        artwork = get_object_or_404(Artwork, pk=pk,user__household=request.user.household)  
        # 子供の誕生日から作成日までの年齢を計算
        def calculate_age(birthdate, creation_date):
            age = relativedelta(creation_date, birthdate)
            return age.years, age.months

        # 誕生日と作成日を使って年齢を計算
        birthdate = artwork.child.birthdate
        creation_date = artwork.creation_date
        age_years, age_months = calculate_age(birthdate, creation_date)

        context = {
            'artwork': artwork,
            'age_years': age_years,
            'age_months': age_months,
        }
        return render(request, self.template_name, context)    
class ArtworkEditView(LoginRequiredMixin, View):
    template_name = 'artwork_edit.html'

    def get(self, request, pk):
        artwork = get_object_or_404(Artwork, pk=pk, user__household=request.user.household) 
        form = ArtworkForm(instance=artwork, user=request.user)
        return render(request, self.template_name, {'form': form, 'artwork': artwork})

    def post(self, request, pk):
        # デバッグ: 現在のユーザーと指定されたpkの確認
        print(f"Logged in user: {request.user}")
        print(f"Requested artwork ID: {pk}")
        artwork = get_object_or_404(Artwork, pk=pk, user__household=request.user.household)
        form = ArtworkForm(request.POST, request.FILES, instance=artwork, user=request.user)
        return render(request, self.template_name, {'form': form, 'artwork': artwork})
        
    def post(self, request, pk):
        artwork = get_object_or_404(Artwork, pk=pk,user__household=request.user.household)
        form = ArtworkForm(request.POST, request.FILES, instance=artwork, user=request.user)    
        if form.is_valid():
            form.save()
            return redirect('app:artwork_detail', pk=artwork.pk)
        return render(request, self.template_name, {'form': form, 'artwork': artwork})
    



class ArtworkDeleteView(LoginRequiredMixin, View):
    template_name = 'artwork_confirm_delete.html'

    def get_object(self, pk, user):
        # userの所属するhouseholdに紐づいたArtworkのみを取得
        return get_object_or_404(Artwork, pk=pk, user__household=user.household)

    def get(self, request, pk):
        # GETリクエストで削除確認画面を表示
        artwork = self.get_object(pk, request.user)
        return render(request, self.template_name, {'artwork': artwork})

    def post(self, request, pk):
        # POSTリクエストで実際に削除処理を行う
        artwork = self.get_object(pk, request.user)
        artwork.delete()
        return redirect(reverse_lazy('app:artwork_list'))  # 削除後にリストページへリダイレクト

class GrowthRecordCreateView(LoginRequiredMixin, View):
    template_name = 'growth_record_form.html'

    def get(self, request):
        form = GrowthRecordForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = GrowthRecordForm(request.POST, user=request.user)
        if form.is_valid():
            growth_record = form.save(commit=False)
            growth_record.user = request.user
            growth_record.household = request.user.household
            growth_record.save()
            return redirect('app:growth_record_list')  # 成功時に一覧画面へ
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
            growth_records = GrowthRecord.objects.filter(child__household=request.user.household).order_by('-measurement_date')
        
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
        record = get_object_or_404(GrowthRecord, pk=pk, child__household=request.user.household)
        form = GrowthRecordForm(instance=record)
        return render(request, self.template_name, {'form': form, 'record': record})

    def post(self, request, pk):
        # 編集対象の成長記録を取得
        record = get_object_or_404(GrowthRecord, pk=pk, child__household=request.user.household)
        form = GrowthRecordForm(request.POST, instance=record)

        # 「保存」ボタンが押された場合
        if 'save' in request.POST and form.is_valid():
            form.save()
            # 成功時に一覧画面へリダイレクト
            return redirect('app:growth_record_list')

        # 「削除」ボタンが押された場合
        elif 'delete' in request.POST:
            # 削除権限の確認（家族のみに制限）
            if record.child.household == request.user.household:
                record.delete()
                # 削除後に一覧画面へリダイレクト
                return redirect('app:growth_record_list')
            else:
                raise PermissionDenied("この記録を削除する権限がありません。")

        # バリデーションエラーがある場合、フォームを再表示
        return render(request, self.template_name, {'form': form, 'record': record})
    
    
class GrowthRecordDeleteView(LoginRequiredMixin, View):
    template_name = 'growth_record_confirm_delete.html'

    def get(self, request, pk):
        record = get_object_or_404(GrowthRecord, pk=pk, child__household=request.user.household)
        return render(request, self.template_name, {'record': record})

    def post(self, request, pk):
        record = get_object_or_404(GrowthRecord, pk=pk, child__household=request.user.household)
        record.delete()
        messages.success(request, '成長記録が削除されました。')
        return redirect('app:growth_record_list')


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        def ensure_datetime(dt):
            if isinstance(dt, date):
                dt = datetime.combine(dt, datetime.min.time())
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            return dt
        
        # 選択された子供の取得
        selected_child_id = request.GET.get('child_id')

        # 子供のリストを取得
        children_list = Children.objects.filter(household=request.user.household)

        # 選択された子供の投稿を取得
        if selected_child_id:
            selected_child = get_object_or_404(Children, id=selected_child_id, household=request.user.household)
            diaries = Diary.objects.filter(child=selected_child, user__household=request.user.household)
            artworks = Artwork.objects.filter(child=selected_child, user__household=request.user.household)
            growth_records = GrowthRecord.objects.filter(child=selected_child, user__household=request.user.household)
        else:
            # 「すべて」を選択した場合、家族のみの投稿（child=None を含む）を表示
            diaries = Diary.objects.filter(user__household=request.user.household).order_by('-entry_date')
            artworks = Artwork.objects.filter(user__household=request.user.household)
            growth_records = GrowthRecord.objects.filter(user__household=request.user.household)

        # 各リストを作成
        diaries_list = [
            {
                'created_at': ensure_datetime(d.entry_date),
                'id': d.id,
                'type': 'diary',
                'child_name': d.child.child_name if d.child else "みんな",  
                'content': d.content,
                'template': d.template.text if d.template else '',
                'first_image': d.medias.filter(media_type='image').first().media_file.url if d.medias.filter(media_type='image').exists() else None,
                'detail_url': reverse('app:diary_detail', args=[d.id]),  # 日記詳細ページへのリンク
            }
            for d in diaries
        ]

        artworks_list = [
            {
                'created_at': ensure_datetime(a.creation_date),
                'id': a.id,
                'type': 'artwork',
                'child_name': a.child.child_name if a.child else "家族作品",
                'title': a.title,
                'image': a.image.url if a.image else None,
                'detail_url': reverse('app:artwork_detail', args=[a.id]),  # 作品詳細ページへのリンク
            }
            for a in artworks
        ]

        growth_records_list = [
            {
                'created_at': ensure_datetime(g.measurement_date),
                'id': g.id,
                'type': 'growth_record',
                'child_name': g.child.child_name,
                'height': g.height,
                'weight': g.weight,
                'memo': g.memo,
                'list_url': reverse('app:growth_record_list'),  # 一覧画面へのリンク
            }
            for g in growth_records
        ]

        # 全ての投稿を1つのリストにまとめてソート
        combined_list = sorted(
            chain(diaries_list, artworks_list, growth_records_list),
            key=lambda x: x['created_at'],
            reverse=True
        )

        return render(request, "home.html", context={
            "combined_list": combined_list,
            "children_list": children_list,
            "selected_child_id": selected_child_id,
        })

# class HomeView(LoginRequiredMixin, View):
#     def get(self, request):
#         def ensure_datetime(dt):
#             if isinstance(dt, date):
#                 dt = datetime.combine(dt, datetime.min.time())
#             if timezone.is_naive(dt):
#                 dt = timezone.make_aware(dt)
#             return dt
        
#         # 選択された子供の取得
#         selected_child_id = request.GET.get('child_id')

#         # 子供のリストを取得
#         children_list = Children.objects.filter(household=request.user.household)

#         # 選択された子供の投稿を取得
#         if selected_child_id:
#             selected_child = get_object_or_404(Children, id=selected_child_id, household=request.user.household)
#             diaries = Diary.objects.filter(child=selected_child, user__household=request.user.household)
#             artworks = Artwork.objects.filter(child=selected_child, user__household=request.user.household)
#             growth_records = GrowthRecord.objects.filter(child=selected_child, user__household=request.user.household)
#         else:
#             # 「すべて」を選択した場合、家族のみの投稿（child=None を含む）を表示
#             diaries = Diary.objects.filter(user__household=request.user.household).order_by('-entry_date')
#             artworks = Artwork.objects.filter(user__household=request.user.household)
#             growth_records = GrowthRecord.objects.filter(user__household=request.user.household)

#         # 各リストを作成
#         diaries_list = [
#             {
#                 'created_at': ensure_datetime(d.entry_date),
#                 'id': d.id,
#                 'type': 'diary',
#                 'child_name': d.child.child_name if d.child else "みんな",  
#                 'content': d.content,
#                 'template': d.template.text if d.template else '',
#                 'first_image': d.medias.filter(media_type='image').first().media_file.url if d.medias.filter(media_type='image').exists() else None,
#                 'detail_url': reverse('app:diary_detail', args=[d.id]),
#             }
#             for d in diaries
#         ]

#         artworks_list = [
#             {
#                 'created_at': ensure_datetime(a.creation_date),
#                 'id': a.id,
#                 'type': 'artwork',
#                 'child_name': a.child.child_name if a.child else "家族作品",
#                 'title': a.title,
#                 'image': a.image.url if a.image else None,
#                 'detail_url': reverse('app:artwork_detail', args=[a.id]),
#             }
#             for a in artworks
#         ]

#         growth_records_list = [
#             {
#                 'created_at': ensure_datetime(g.measurement_date),
#                 'id': g.id,
#                 'type': 'growth_record',
#                 'child_name': g.child.child_name,
#                 'height': g.height,
#                 'weight': g.weight,
#                 'memo': g.memo,
#                 'list_url': reverse('app:growth_record_list'),
#             }
#             for g in growth_records
#         ]

#         # 全ての投稿を1つのリストにまとめてソート
#         combined_list = sorted(
#             chain(diaries_list, artworks_list, growth_records_list),
#             key=lambda x: x['created_at'],
#             reverse=True
#         )

#         return render(request, "home.html", context={
#             "combined_list": combined_list,
#             "children_list": children_list,
#             "selected_child_id": selected_child_id,
#         })
    
