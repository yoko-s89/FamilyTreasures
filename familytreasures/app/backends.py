from typing import Any
from django.contrib.auth.backends import BaseBackend
from django.http import HttpRequest
from app.models import User
from django.contrib.auth import get_user_model

class UserAuthBackend(BaseBackend):
    def authenticate(self, request: HttpRequest, email: str = None, password: str = None, **kwargs) -> Any:
        # emailが指定されていれば使い、そうでなければusernameを使う
        # email = kwargs.get('email') or username
        print("UserAuthBackendが呼び出された")
        
        try:
            # emailが指定されていれば、それを使ってユーザーを取得
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

class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None