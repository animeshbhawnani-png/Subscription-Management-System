from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    RegisterSerializer,
    StaffCreateSerializer,
    UserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .permissions import IsAdmin

User = get_user_model()


def _ok(data):
    return Response({"data": data, "error": None}, status=status.HTTP_200_OK)


def _created(data):
    return Response({"data": data, "error": None}, status=status.HTTP_201_CREATED)


def _err(message, code=status.HTTP_400_BAD_REQUEST):
    return Response({"data": None, "error": message}, status=code)


class RegisterView(APIView):
    """POST /api/auth/register/ — customer self-registration."""
    permission_classes = [AllowAny]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        if not s.is_valid():
            return _err(s.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)
        user = s.save()
        return _created(UserSerializer(user).data)


class MeView(APIView):
    """GET /api/auth/me/ — current authenticated user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return _ok(UserSerializer(request.user).data)


class StaffCreateView(APIView):
    """POST /api/auth/staff/ — admin creates a staff account."""
    permission_classes = [IsAdmin]

    def post(self, request):
        s = StaffCreateSerializer(data=request.data)
        if not s.is_valid():
            return _err(s.errors, status.HTTP_422_UNPROCESSABLE_ENTITY)
        user = s.save()
        return _created(UserSerializer(user).data)


class PasswordResetRequestView(APIView):
    """POST /api/auth/password-reset/ — send reset link to email."""
    permission_classes = [AllowAny]

    def post(self, request):
        s = PasswordResetRequestSerializer(data=request.data)
        if not s.is_valid():
            return _err(s.errors)

        email = s.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal whether the email exists
            return _ok({"detail": "If that email is registered, a reset link has been sent."})

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        # shortcut: reset URL uses localhost; replace with production domain when deploying
        reset_url = f"http://localhost:5173/reset-password?uid={uid}&token={token}"

        send_mail(
            subject="Brightloop — Password Reset",
            message=f"Click the link to reset your password:\n\n{reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return _ok({"detail": "If that email is registered, a reset link has been sent."})


class PasswordResetConfirmView(APIView):
    """POST /api/auth/password-reset/confirm/ — set new password via token."""
    permission_classes = [AllowAny]

    def post(self, request):
        s = PasswordResetConfirmSerializer(data=request.data)
        if not s.is_valid():
            return _err(s.errors)

        uid = s.validated_data["uid"]
        token = s.validated_data["token"]
        new_password = s.validated_data["new_password"]

        try:
            pk = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValueError, TypeError):
            return _err("Invalid reset link.", status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return _err("Reset link is expired or invalid.", status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return _ok({"detail": "Password updated successfully."})
