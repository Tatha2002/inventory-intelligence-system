from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .jwt_utils import decode_token
from .models import User


class JWTAuthentication(BaseAuthentication):
    
    def authenticate(self, request):

        # Get Authorization header
        auth_header = request.headers.get('Authorization')

        # If no token is provided, let DRF handle anonymous access
        if not auth_header:
            return None

        # Expected format: Bearer <token>
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise AuthenticationFailed("Invalid authorization header format.")

        token = parts[1]

        try:

            # Decode and verify access token
            payload = decode_token(token,token_type='access')

        except ValueError as error:
            raise AuthenticationFailed(str(error))

        # Get user from database
        try:

            user = User.objects.get(id=payload['user_id'])

        except User.DoesNotExist:
            raise AuthenticationFailed("User does not exist.")

        # Check whether account is active
        if not user.is_active:
            raise AuthenticationFailed("User account is inactive.")

        # Return authenticated user and token
        return (user, token)
    

    def authenticate_header(self, request):
        return 'Bearer'
