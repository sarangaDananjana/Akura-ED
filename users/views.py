from rest_framework import viewsets, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from .serializers import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer, UserSerializer, UserCreateSerializer

User = get_user_model()

# --- Public & Auth Views ---


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login endpoint generating JWT."""
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """Refresh endpoint preserving custom claims."""
    serializer_class = CustomTokenRefreshSerializer


class RegisterView(generics.CreateAPIView):
    """Endpoint for user registration."""
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserCreateSerializer


class UserMeView(APIView):
    """Endpoint for retrieving and updating the current user's profile."""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
