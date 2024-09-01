from django.urls import path
from .views import HomeView,SignupView,LoginView

app_name = 'app'

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('signup/', SignupView.as_view(), name="signup"),
    path('login/', LoginView.as_view(), name="login"),
]