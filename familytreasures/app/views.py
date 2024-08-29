from django.shortcuts import render
from django.views import View
from app.forms import SignupForm
# Create your views here.

class SignupView(View):
    def get(self, request):
        form = SignupForm()
        return render(request, "signup.html", context={
            "form":form
        })
        
class LoginView(View):
    def get(self, request):
        return render(request, "login.html")
    

class HomeView(View):
    # login_url = "login"
    def get(self, request):
        return render(request, "home.html")