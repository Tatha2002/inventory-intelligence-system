import jwt
import uuid
from datetime import datetime, timezone
from django.conf import settings


# Generate Access Token
def generate_access_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,

        'token_type': 'access',

        'iat': now,
        'exp': now + settings.JWT_ACCESS_TOKEN_LIFETIME,
    }
    token = jwt.encode(payload,settings.JWT_SECRET_KEY,algorithm=settings.JWT_ALGORITHM)

    return token


# Generate Refresh Token
def generate_refresh_token(user):
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    expires_at = now + settings.JWT_REFRESH_TOKEN_LIFETIME

    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,

        'token_type': 'refresh',
        'jti': jti,

        'iat': now,
        'exp': expires_at,
    }

    token = jwt.encode(
        payload,
        settings.JWT_REFRESH_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return {
        'token': token,
        'jti': jti,
        'expires_at': expires_at,
    }


# Decode and Verify JWT
def decode_token(token, token_type='access'):

    if token_type == 'access':
        secret_key = settings.JWT_SECRET_KEY

    elif token_type == 'refresh':
        secret_key = settings.JWT_REFRESH_SECRET_KEY

    else:
        raise ValueError("Invalid token type.")

    try:

        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                'require': [
                    'exp',
                    'iat',
                    'user_id',
                    'email',
                    'role',
                    'token_type'
                ]
            }
        )

        # Verify token type
        if payload.get('token_type') != token_type:
            raise ValueError("Incorrect token type.")

        # Validate user ID
        if not isinstance(payload.get('user_id'), int):
            raise ValueError("Invalid user ID.")

        # Refresh token must contain JTI
        if token_type == 'refresh' and not payload.get('jti'):
            raise ValueError("Refresh token JTI is missing.")

        return payload

    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired.")

    except jwt.InvalidTokenError:
        raise ValueError("Invalid token.")
