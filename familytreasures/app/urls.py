from django.urls import path
from .views import HomeView,SignupView,LoginView,ChildrenListView, ChildrenCreateView, ChildrenUpdateDeleteView, DiaryCreateView, DiaryListView, DiaryDetailView

app_name = 'app'

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('signup/', SignupView.as_view(), name="signup"),
    path('login/', LoginView.as_view(), name="login"),
    path('children/', ChildrenListView.as_view(), name='children_list'),  # リスト表示
    path('children/add/', ChildrenCreateView.as_view(), name='children_add'),  # 子供の追加
    path('children/update_delete/<int:pk>/', ChildrenUpdateDeleteView.as_view(), name='children_update_delete'),
    path('diary/new/', DiaryCreateView.as_view(), name='diary_new'),# 日記新規作成ページ
    path('diaries/', DiaryListView.as_view(), name='diary_list'),  # 日記一覧画面
    path('diary/<int:pk>/', DiaryDetailView.as_view(), name='diary_detail'),  # 日記詳細ページ
]
