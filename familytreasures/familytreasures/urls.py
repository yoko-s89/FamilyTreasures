from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app.views import InviteSignupView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('app.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('join/<str:token>/', InviteSignupView.as_view(), name='signup_from_invitation'),  
    # path('', portfolio, name='portfolio')ポートフォリオ作成時に使用
]

if settings.DEBUG:  # DEBUGがTrueのときだけ適用
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)