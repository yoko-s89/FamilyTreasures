from django.contrib import admin
from django.urls import path, include
from app.views import SignupView,LoginView,HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', SignupView.as_view(), name="signup"),
    path('', LoginView.as_view(), name="login"),
    path('home/', HomeView.as_view(), name="home"),
    path('app/', include('app.urls'))
]
