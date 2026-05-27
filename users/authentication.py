from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Returns the user model instance associated with the token, if active,
        and enforces the single-session policy by checking `auth_version`.
        """
        user = super().get_user(validated_token)
        
        # Enforce single session restriction
        token_auth_version = validated_token.get('auth_version')
        if token_auth_version and str(user.auth_version) != token_auth_version:
            raise AuthenticationFailed(
                _('User logged in from another device. Session invalidated.'),
                code='user_logged_in_elsewhere',
            )
            
        return user
