from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('app.urls'))
    # path('', portfolio, name='portfolio')ポートフォリオ作成時に使用
]
