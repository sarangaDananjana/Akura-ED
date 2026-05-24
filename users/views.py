from rest_framework import viewsets, generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import CustomTokenObtainPairSerializer, UserSerializer, UserCreateSerializer

User = get_user_model()

# --- Public & Auth Views ---


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login endpoint generating JWT."""
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """Endpoint for user registration."""
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserCreateSerializer

# --- Custom Admin Panel Views ---


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    API for the Custom Admin Panel to manage users.
    Requires Admin (is_staff=True) privileges.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    # IsAdminUser ensures only users with is_staff=True can access these endpoints.
