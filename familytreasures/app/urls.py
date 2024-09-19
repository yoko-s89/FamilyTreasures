from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from .views import (
    HomeView,SignupView,LoginView, ChildrenCreateView, ChildrenUpdateDeleteView,
    DiaryCreateView, DiaryListView, DiaryDetailView, CommentCreateView, CommentEditView,
    CommentDeleteView, DiaryEditView, DiaryDeleteView, ArtworkCreateView, ArtworkListView, 
    ArtworkDetailView, ArtworkEditView, ArtworkDeleteView, GrowthRecordListView, 
    GrowthRecordCreateView, GrowthRecordUpdateView,  my_page, family_delete, create_invitation_view,
    use_invitation, use_invitation, InviteSignupView, family_delete_confirm, DeleteMediaView
)
from . import views

app_name = 'app'

urlpatterns = [
    #ホームページ
    path('home/', HomeView.as_view(), name='home'),
    #ユーザー認証
    path('signup/', SignupView.as_view(), name="signup"),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
    #アカウント情報更新
    path('account/update//', views.account_update, name='account_update'),
    #マイページ
    path('my_page/', views.my_page, name='my_page'),
    path('image_update/', views.image_update, name='image_update'),
    path('image_delete/', views.image_delete, name='image_delete'),
    #家族招待
    path('create_invitation/', create_invitation_view, name='create_invitation'),
    path('join/<uuid:token>/', use_invitation, name='use_invitation'),  # 招待URLのパターン
    # path('join/<str:token>/', InviteSignupView.as_view(), name='signup_from_invitation'),

    #家族削除
    path('family_delete/<int:id>/', family_delete, name='family_delete'),  
    path('family_delete_confirm/<int:id>/', family_delete_confirm, name='family_delete_confirm'),
    
    #子供
    path('children/add/', ChildrenCreateView.as_view(), name='children_add'),  # 追加
    path('children/update_delete/<int:pk>/', ChildrenUpdateDeleteView.as_view(), name='children_update_delete'),
    #日記
    path('diary/new/', DiaryCreateView.as_view(), name='diary_new'),# 日記新規作成ページ
    path('diaries/', DiaryListView.as_view(), name='diary_list'),  # 日記一覧画面
    path('diary/<int:pk>/', DiaryDetailView.as_view(), name='diary_detail'),  # 日記詳細ページ
    path('diary/<int:pk>/edit/', DiaryEditView.as_view(), name='diary_edit'),
    path('diary/media/<int:media_pk>/delete/', DiaryEditView.as_view(), name='diary_media_delete'),  # メディア削除のためのURL
    path('diary/<int:pk>/media/<int:media_pk>/delete/', DeleteMediaView.as_view(), name='diary_media_delete'),
    path('diary/<int:pk>/delete/', DiaryDeleteView.as_view(), name='diary_delete'),
    #コメント
    path('diary/<int:diary_id>/comment/', CommentCreateView.as_view(), name='comment_create'),
    path('comment/<int:pk>/edit/', CommentEditView.as_view(), name='comment_edit'),  # コメント編集用URL
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),  # コメント削除用URL
    #制作物
    path('artwork/new/', ArtworkCreateView.as_view(), name='artwork_create'),
    path('artwork/', ArtworkListView.as_view(), name='artwork_list'),
    path('artwork/<int:pk>/', ArtworkDetailView.as_view(), name='artwork_detail'),
    path('artwork/<int:pk>/edit/', ArtworkEditView.as_view(), name='artwork_edit'),
    path('artwork/<int:pk>/delete/', ArtworkDeleteView.as_view(), name='artwork_delete'),
    #成長記録
    path('growth_record/add/', GrowthRecordCreateView.as_view(), name='growth_record_add'),
    path('growth_records/', GrowthRecordListView.as_view(), name='growth_record_list'),
    path('growth_records/update/<int:pk>/', GrowthRecordUpdateView.as_view(), name='growth_record_update'),
    # UUIDパターンを追加
    re_path(r'^join/(?P<token>[0-9a-fA-F-]{36})/$', InviteSignupView.as_view(), name='signup_from_invitation'),
]

