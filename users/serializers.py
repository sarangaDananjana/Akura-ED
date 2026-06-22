from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings
from django.utils.translation import gettext_lazy as _
import uuid

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT Serializer to include extra user data in the token payload."""
    @classmethod
    def get_token(cls, user):
        # Rotate auth_version on login to invalidate old sessions
        user.auth_version = uuid.uuid4()
        user.save(update_fields=['auth_version'])

        token = super().get_token(user)
        # Add custom claims
        token['auth_version'] = str(user.auth_version)
        token['is_staff'] = user.is_staff
        token['is_premium'] = user.is_premium
        return token


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """Custom Refresh Serializer to check auth_version and inject claims."""
    def validate(self, attrs):
        data = super().validate(attrs)
        
        refresh = RefreshToken(attrs['refresh'])
        user_id = refresh.payload.get('user_id')
        user = User.objects.get(id=user_id)
        
        # Check if the session was invalidated by another login
        if refresh.payload.get('auth_version') != str(user.auth_version):
            raise AuthenticationFailed(
                _('User logged in from another device. Session invalidated.'),
                code='user_logged_in_elsewhere',
            )

        # Inject custom claims into the new access token
        access = refresh.access_token
        access['auth_version'] = str(user.auth_version)
        access['is_staff'] = user.is_staff
        access['is_premium'] = user.is_premium
        data['access'] = str(access)
        
        # If rotation is enabled, also inject into the new refresh token
        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            
            refresh['auth_version'] = str(user.auth_version)
            refresh['is_staff'] = user.is_staff
            refresh['is_premium'] = user.is_premium
            data['refresh'] = str(refresh)
            
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_premium',
                  'daily_flashcard_limit', 'is_staff', 'is_active', 'profile_photo')
        read_only_fields = ('id',)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', '')
        )
        return user
