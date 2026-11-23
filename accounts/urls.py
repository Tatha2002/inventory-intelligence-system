from django.urls import path
from .api_views import RegisterAPIView, VerifyOTPAPIView, LoginAPIView, RefreshTokenAPIView, LogoutAPIView, UserProfileAPIView
from .views import portal_register, portal_verify_otp, portal_login, portal_logout, portal_dashboard, store_manager_dashboard

urlpatterns = [
    # REST API AUTHENTICATION
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify-otp'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('refresh/', RefreshTokenAPIView.as_view(), name='refresh'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('profile/', UserProfileAPIView.as_view(), name='profile'),

    # HTML PORTAL AUTHENTICATION
    path('portal/register/', portal_register, name='portal-register'),
    path('portal/verify-otp/', portal_verify_otp, name='portal-verify-otp'),
    path('portal/login/', portal_login, name='portal-login'),
    path('portal/logout/', portal_logout, name='portal-logout'),
    path('portal/dashboard/', portal_dashboard, name='portal-dashboard'),
    path('store-manager/dashboard/', store_manager_dashboard, name='store-manager-dashboard'),
]




# POST http://127.0.0.1:8000/accounts/register/
# POST http://127.0.0.1:8000/accounts/verify-otp/
# POST http://127.0.0.1:8000/accounts/login/
# POST http://127.0.0.1:8000/accounts/refresh/
# POST http://127.0.0.1:8000/accounts/logout/
# GET http://127.0.0.1:8000/accounts/profile/



