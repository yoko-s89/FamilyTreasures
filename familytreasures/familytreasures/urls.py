from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app.views import InviteSignupView, PortfolioView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('app.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('join/<str:token>/', InviteSignupView.as_view(), name='signup_from_invitation'), 
    path('', PortfolioView.as_view(), name='portfolio'), 
]

if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)