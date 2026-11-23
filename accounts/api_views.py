
import secrets
from datetime import timedelta
import jwt

from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import User, EmailOTP, RefreshToken
from .jwt_utils import generate_access_token, generate_refresh_token, decode_token
from .authentication import JWTAuthentication
from .permissions import IsStoreManagerOrInventoryStaff


# REGISTER API
class RegisterAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip().lower()
        phone = request.data.get('phone', '').strip()
        password = request.data.get('password')
        role = request.data.get('role')

        if not all([name, email, phone, password, role]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email address"}, status=status.HTTP_400_BAD_REQUEST)

        allowed_roles = [User.Role.STORE_MANAGER, User.Role.INVENTORY_STAFF]

        if role not in allowed_roles:
            return Response({"error": "Invalid role. Choose STORE_MANAGER or INVENTORY_STAFF"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email__iexact=email).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone=phone).exists():
            return Response({"error": "Phone number already registered"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password)
        except ValidationError as error:
            return Response({"error": error.messages}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                user = User.objects.create_user(email=email, password=password, name=name, phone=phone, role=role, is_active=False, is_email_verified=False)
                otp = str(secrets.randbelow(900000) + 100000)
                otp_obj = EmailOTP(user=user, expires_at=timezone.now() + timedelta(minutes=5))
                otp_obj.set_otp(otp)
                otp_obj.save()

                send_mail(subject="Inventory Portal Email Verification OTP", message=f"Hello {name},\n\nYour verification OTP is {otp}.\nIt expires in 5 minutes.", from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email], fail_silently=False)

            return Response({"message": "Registration successful. Please verify your email.", "email": email, "role": role}, status=status.HTTP_201_CREATED)

        except Exception:
            return Response({"error": "Registration failed. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# VERIFY OTP API
class VerifyOTPAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        otp = request.data.get('otp', '').strip()

        if not email or not otp:
            return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email address"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user = User.objects.select_for_update().filter(email__iexact=email).first()

            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            if user.is_email_verified:
                return Response({"message": "Email is already verified"}, status=status.HTTP_200_OK)

            otp_obj = EmailOTP.objects.select_for_update().filter(user=user, is_used=False).order_by('-created_at').first()

            if not otp_obj:
                return Response({"error": "OTP not found. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)

            if not otp_obj.verify_otp(otp):
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

            otp_obj.is_used = True
            otp_obj.save(update_fields=['is_used'])
            EmailOTP.objects.filter(user=user, is_used=False).update(is_used=True)

            user.is_email_verified = True
            user.is_active = True
            user.save(update_fields=['is_email_verified', 'is_active'])

        return Response({"message": "Email verified successfully. Account activated.", "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}}, status=status.HTTP_200_OK)


# LOGIN API
class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email__iexact=email).first()

        if not user or not user.check_password(password):
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.role not in [User.Role.STORE_MANAGER, User.Role.INVENTORY_STAFF]:
            return Response({"error": "This account cannot use the inventory API login"}, status=status.HTTP_403_FORBIDDEN)

        if not user.is_email_verified:
            return Response({"error": "Please verify your email first"}, status=status.HTTP_403_FORBIDDEN)

        if not user.is_active:
            return Response({"error": "Your account is inactive"}, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                access_token = generate_access_token(user)
                refresh_data = generate_refresh_token(user)
                RefreshToken.objects.create(user=user, jti=refresh_data['jti'], expires_at=refresh_data['expires_at'])

            return Response({"message": "Login successful", "user": {"id": user.id, "name": user.name, "email": user.email, "phone": user.phone, "role": user.role}, "tokens": {"access": access_token, "refresh": refresh_data['token'], "token_type": "Bearer"}}, status=status.HTTP_200_OK)

        except Exception:
            return Response({"error": "Login failed. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# REFRESH TOKEN API
class RefreshTokenAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = decode_token(refresh_token, token_type='refresh')
            user_id = payload['user_id']
            jti = payload['jti']

            token_obj = RefreshToken.objects.select_related('user').filter(jti=jti).first()

            if not token_obj or not token_obj.is_valid:
                return Response({"error": "Refresh token is revoked or expired"}, status=status.HTTP_401_UNAUTHORIZED)

            if token_obj.user_id != user_id:
                return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

            user = token_obj.user

            if not user.is_active or not user.is_email_verified or user.role not in [User.Role.STORE_MANAGER, User.Role.INVENTORY_STAFF]:
                return Response({"error": "Account is inactive, unverified or unauthorized"}, status=status.HTTP_403_FORBIDDEN)

            access_token = generate_access_token(user)

            return Response({"message": "Access token refreshed successfully", "access": access_token, "token_type": "Bearer"}, status=status.HTTP_200_OK)

        except (ValueError, jwt.InvalidTokenError, KeyError, TypeError):
            return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


# LOGOUT API
class LogoutAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = decode_token(refresh_token, token_type='refresh')
            jti = payload['jti']
            user_id = payload['user_id']

            with transaction.atomic():
                token_obj = RefreshToken.objects.select_for_update().filter(jti=jti, user_id=user_id).first()

                if not token_obj:
                    return Response({"error": "Refresh token not found"}, status=status.HTTP_401_UNAUTHORIZED)

                if token_obj.revoked_at is not None:
                    return Response({"message": "Already logged out"}, status=status.HTTP_200_OK)

                token_obj.revoked_at = timezone.now()
                token_obj.save(update_fields=['revoked_at'])

            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

        except (ValueError, jwt.InvalidTokenError, KeyError, TypeError):
            return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


# USER PROFILE API
class UserProfileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsStoreManagerOrInventoryStaff]

    def get(self, request):
        user = request.user

        return Response({"message": "Profile fetched successfully", "user": {"id": user.id, "name": user.name, "email": user.email, "phone": user.phone, "employee_code": user.employee_code, "role": user.role, "is_email_verified": user.is_email_verified}}, status=status.HTTP_200_OK)
