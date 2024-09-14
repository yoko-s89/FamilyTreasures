from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from app.forms import SignupForm, LoginForm, ChildrenForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin,  UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from .models import Children, Diary, DiaryMedia, Child, Comment
from .forms import ChildrenForm, DiaryForm, DiaryMediaForm, CommentForm
# from app.models import User  # Userモデルを直接インポート
from django.contrib.auth import get_user_model  # get_user_modelを使用
User = get_user_model()
from django.contrib import messages
from django.db.models import Q


# Create your views here.

class SignupView(View):
    def get(self, request):
        form = SignupForm()
        return render(request, "signup.html", context={
            "form":form
        })
    def post(self, request):
        print(request.POST)
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("app:home")
        return render(request, "signup.html", context={
            "form": form
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
    login_url = "login"
    def get(self, request):
        return render(request, "home.html")
    
class ChildrenListView(View):
    def get(self, request):
        # モデルからデータを取得
        children_list = Children.objects.all()

        # データをテンプレートに渡してレンダリング
        return render(request, "children_list.html", context={
            "children_list": children_list
        })

# 子供の情報作成
class ChildrenCreateView(View):
    def get(self, request):
        # 空のフォームを生成してテンプレートに渡す
        form = ChildrenForm()
        return render(request, "children_form.html", context={
            "form": form
            })

    def post(self, request):
        # POSTデータでフォームを生成
        form = ChildrenForm(request.POST)
        if form.is_valid():
            # フォームが有効な場合、データを保存
            form.save()
            return redirect("app:children_list")  # 成功時にリダイレクト
        # フォームが無効な場合、エラーとともにフォームを再表示
        return render(request, "children_form.html", context={
            "form": form
            })

#子供の編集と削除
class ChildrenUpdateDeleteView(View):
    def get(self, request, pk):
        # 子供のデータが存在しない場合の処理
        if not Children.objects.exists():
            # データがなければ追加ページにリダイレクト
            return redirect("app:children_add")

        # 存在する場合は子供データを取得し、フォームに表示
        child = get_object_or_404(Children, pk=pk)
        form = ChildrenForm(instance=child)
        return render(request, "children_form_delete.html", context={
            "form": form,
            "child": child
        })

    def post(self, request, pk):
        # 子供のデータが存在しない場合の処理
        if not Children.objects.exists():
            # データがなければ追加ページにリダイレクト
            return redirect("app:children_add")

        # 更新または削除の処理
        child = get_object_or_404(Children, pk=pk)

        if 'update' in request.POST:
            form = ChildrenForm(request.POST, instance=child)
            if form.is_valid():
                form.save()
                return redirect("app:children_list")
        elif 'delete' in request.POST:
            child.delete()
            return redirect('children_list')

        return render(request, "children_form_delete.html", context={
            "form": form,
            "child": child
        })
class ChildrenUpdateDeleteView(View):
    def get(self, request, pk=None):
        # 子供のデータが存在しない場合はメッセージを表示
        if not Children.objects.exists():
            return render(request, "no_children.html")

        # 存在する場合は通常通りデータを取得
        child = get_object_or_404(Children, pk=pk)
        form = ChildrenForm(instance=child)
        return render(request, "children_form_delete.html", context={
            "form": form,
            "child": child
        })

    def post(self, request, pk=None):
        # 子供のデータが存在しない場合はメッセージを表示
        if not Children.objects.exists():
            return render(request, "no_children.html")

        # 存在する場合の更新・削除処理
        child = get_object_or_404(Children, pk=pk)

        if 'update' in request.POST:
            form = ChildrenForm(request.POST, instance=child)
            if form.is_valid():
                form.save()
                return redirect('children_list')
        elif 'delete' in request.POST:
            child.delete()
            return redirect('children_list')

        return render(request, "children_form_delete.html", context={
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
    
    # template_name = 'diary_form.html'
    # # success_url = reverse_lazy('diary_list')  # 投稿完了後のリダイレクト先
    
    # def get(self, request, *args, **kwargs):
    #     # DiaryFormとDiaryMediaFormをテンプレートに渡す
    #     form = DiaryForm()
    #     media_form = DiaryMediaForm()
    #     return render(request, self.template_name, {'form': form, 'media_form': media_form})

    
    # def post(self, request, *args, **kwargs):
    #     form = DiaryForm(request.POST)  
    #     media_files = request.FILES.getlist('media_url')  # 複数のファイルを取得

    #     if form.is_valid():
    #         diary = form.save(commit=False)  # データベースに保存せずにインスタンスを作成
    #         diary.user = request.user  # ログインユーザーを日記に関連付ける
    #         diary.save()  # 日記データを保存
            
    #         for media_file in media_files:
    #             media = DiaryMedia(diary=diary, media_url=media_file)
    #             media.media_type = 'image' if media_file.content_type.startswith('image') else 'video'
    #             media.save()


            # メディアの保存（もしメディアもフォームで受け取るなら）
            # media_form = DiaryMediaForm(request.POST, request.FILES)
            # if media_form.is_valid():
            #     media = media_form.save(commit=False)
            #     media.diary = diary
            #     media.save()

        return redirect('diary_list')  # 成功したら一覧画面へリダイレクト
        
        return render(request, self.template_name, {
            'form': form,
            'errors': form.errors
        })

    
# class DiaryListView(View):
#     model = Diary
#     template_name = 'diary_list.html'  # 一覧ページのテンプレート
#     context_object_name = 'diaries'  # テンプレートで使う変数名

#     def get(self, request):
#         selected_child = request.GET.get('child')
#         # 日記を新しい順に取得
#         diaries = Diary.objects.all().order_by('-created_at')
        
#         if selected_child:
#             diaries = diaries.filter(child__id=selected_child)


#         # 子供の選択用プルダウンのために子供のリストを取得
#         children = Children.objects.all()
        
#         # 各日記に関連する最初の画像を取得
#         for diary in diaries:
#             first_image = diary.diarymedia_set.filter(media_type='image').first()
#             diary.first_image = first_image  # テンプレートで使用できるように属性として設定

#         return render(request, 'diary_list.html', {
#             'diaries': diaries,
#             'children': children,
#             'selected_child': selected_child
#         })

class DiaryListView(View):
    template_name = 'diary_list.html'  # 一覧ページのテンプレート

    def get(self, request):
        selected_child = request.GET.get('child')
        
        # 日記を新しい順に取得
        diaries = Diary.objects.all().order_by('-created_at')
        
        # 子供が選択された場合
        if selected_child:
            # 選択された子供の日記、もしくは子供が選択されていない日記を表示
            diaries = diaries.filter(Q(child__id=selected_child) | Q(child__isnull=True))
        else:
            # 全ての日記を表示（子供がいないものも含む）
            diaries = diaries.filter(Q(child__isnull=True) | Q(child__isnull=False))

        # 子供の選択用プルダウンのために子供のリストを取得
        children = Children.objects.all()

        # 各日記に関連する最初の画像を取得
        for diary in diaries:
            first_image = diary.diarymedia_set.filter(media_type='image').first()
            diary.first_image = first_image  # テンプレートで使用できるように属性として設定

        return render(request, self.template_name, {
            'diaries': diaries,
            'children': children,
            'selected_child': selected_child,
        })   
class DiaryDetailView(View):
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
