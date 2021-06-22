"""pesa_exchange URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from rest_framework import routers
from rest_framework.authtoken import views

from pesa_exchange.users.views import UserViewSet, UserRegisterViewSet, LoginViewSet
from pesa_exchange.currency.views import CurrencyViewSet
from pesa_exchange.wallet.views import WalletViewSet

 

router = routers.SimpleRouter()

router.register(r'users', UserViewSet)
router.register(r'users/register', UserRegisterViewSet, basename='auth-register')
router.register(r'auth/login', LoginViewSet, basename='auth-login')

router.register(r'wallet', WalletViewSet)
router.register(r'currencies', CurrencyViewSet)


# urlpatterns = router.urls
urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]

