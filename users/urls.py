from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomTokenObtainPairView, CustomTokenRefreshView, RegisterView, AdminUserViewSet, UserMeView, ForgotPasswordView, ResetPasswordView

# Router for ViewSets
router = DefaultRouter()
router.register(r'admin/users', AdminUserViewSet, basename='admin-users')

urlpatterns = [
    # Auth endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('auth/login/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/me/', UserMeView.as_view(), name='user_me'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    # Admin API endpoints
    path('', include(router.urls)),
]
