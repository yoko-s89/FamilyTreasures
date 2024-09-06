from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from app.forms import SignupForm, LoginForm, ChildrenForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Children
from .forms import ChildrenForm 

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