from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from app.forms import SignupForm, LoginForm, ChildrenForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Children, Diary, DiaryMedia, Child, Comment
from .forms import ChildrenForm, DiaryForm, DiaryMediaForm, CommentForm
# from app.models import User  # Userモデルを直接インポート
from django.contrib.auth import get_user_model  # get_user_modelを使用

User = get_user_model()


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
        return render(request, "login.html")
    def post(self, request):
        print(request.POST)
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("app:home")
        return render(request, "login.html", context={
            "form": form
        })

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
    success_url = reverse_lazy('diary_list')  # 投稿完了後のリダイレクト先
    
    def get(self, request, *args, **kwargs):
        form = DiaryForm()  # 日記フォーム
        media_form = DiaryMediaForm()  # メディアフォーム
        return render(request, self.template_name, {'form': form, 'media_form': media_form})

    def get(self, request, *args, **kwargs):
        # 子供のリストを取得してフォームに渡す
        form = DiaryForm()
        return render(request, self.template_name, {'form': form})
    
    def get(self, request, *args, **kwargs):
        form = DiaryForm()  # DiaryFormには定型文とスタンプのプルダウンメニューも含まれる
        return render(request, self.template_name, {'form': form})

    
    def post(self, request, *args, **kwargs):
        form = DiaryForm(request.POST)  
        media_files = request.FILES.getlist('media_url')  # 複数のファイルを取得

        if form.is_valid():
            diary = form.save(commit=False)  # データベースに保存せずにインスタンスを作成
            diary.user = request.user  # ログインユーザーを日記に関連付ける
            diary.save()  # 日記データを保存
            
            for media_file in media_files:
                media = DiaryMedia(diary=diary, media_url=media_file)
                media.media_type = 'image' if media_file.content_type.startswith('image') else 'video'
                media.save()


            # メディアの保存（もしメディアもフォームで受け取るなら）
            # media_form = DiaryMediaForm(request.POST, request.FILES)
            # if media_form.is_valid():
            #     media = media_form.save(commit=False)
            #     media.diary = diary
            #     media.save()

        return redirect(self.success_url)  # 成功したらリダイレクト

        # バリデーションに失敗した場合、エラーメッセージと共にフォームを再表示
        return render(request, self.template_name, {
            'form': form,
            'errors': form.errors
            })
class DiaryListView(View):
    def get(self, request):
        selected_child = request.GET.get('child')
        # 日記を新しい順に取得
        diaries = Diary.objects.all().order_by('-created_at')
        
        if selected_child:
            diaries = diaries.filter(child__id=selected_child)


        # 子供の選択用プルダウンのために子供のリストを取得
        children = Children.objects.all()
        
        # 各日記に関連する最初の画像を取得
        for diary in diaries:
            first_image = diary.diarymedia_set.filter(media_type='image').first()
            diary.first_image = first_image  # テンプレートで使用できるように属性として設定

        return render(request, 'diary_list.html', {
            'diaries': diaries,
            'children': children,
            'selected_child': selected_child
        })

class DiaryDetailView(View):
    def get(self, request, pk):
        diary = get_object_or_404(Diary, pk=pk)
        comments = Comment.objects.filter(diary=diary).order_by('-created_at')
        return render(request, "diary_detail.html", context={
            "diary": diary,
            "comments": comments
        })
        
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
            return redirect('diary_detail', pk=diary_id)
        return render(request, "comment_form.html", context={
            "form": form,
            "diary": diary
        })