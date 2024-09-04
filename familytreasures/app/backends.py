from typing import Any
from django.contrib.auth.backends import BaseBackend
from django.http import HttpRequest
from app.models import User

class UserAuthBackend(BaseBackend):
    def authenticate(self, request: HttpRequest, username: str = None, password: str = None, **kwargs) -> Any:
        # emailが指定されていれば使い、そうでなければusernameを使う
        email = kwargs.get('email') or username
        print("UserAuthBackendが呼び出された")
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
    
    def get_user(self, user_id: int) -> Any:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
