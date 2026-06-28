from rest_framework import viewsets, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model, authenticate
from django.core.cache import cache
from django.shortcuts import render
from django.views import View
from .serializers import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer, UserSerializer, UserCreateSerializer
from .utils import generate_otp_code, send_otp_sms

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

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ForgotPasswordView(APIView):
    """Generates an OTP and sends it via SMS for password reset."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        phone_number = request.data.get('phone_number')

        if not username or not phone_number:
            return Response({"detail": "Username and phone number are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username, phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"detail": "No user found with this username and phone number."}, status=status.HTTP_404_NOT_FOUND)

        otp = generate_otp_code()
        # Save OTP in cache for 5 minutes
        cache.set(f"password_reset_otp_{username}", otp, timeout=300)
        
        success = send_otp_sms(phone_number, otp)
        if success:
            return Response({"detail": "OTP sent successfully."})
        else:
            return Response({"detail": "Failed to send OTP. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordView(APIView):
    """Verifies OTP and resets the password."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not username or not otp or not new_password:
            return Response({"detail": "Username, OTP, and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

        cached_otp = cache.get(f"password_reset_otp_{username}")
        if not cached_otp or cached_otp != str(otp):
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()
        
        # Clear the OTP from cache
        cache.delete(f"password_reset_otp_{username}")

        return Response({"detail": "Password reset successfully."})


# --- Custom Admin Panel Views ---

class DeleteAccountWebView(View):
    """Web view for users to delete their account by providing credentials."""
    
    def get(self, request):
        return render(request, 'delete_account.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            user.delete()
            return render(request, 'delete_account.html', {'success': True})
        else:
            return render(request, 'delete_account.html', {'error': 'Invalid username or password.'})

class AdminUserViewSet(viewsets.ModelViewSet):
    """
    API for the Custom Admin Panel to manage users.
    Requires Admin (is_staff=True) privileges.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    # IsAdminUser ensures only users with is_staff=True can access these endpoints.
