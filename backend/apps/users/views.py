from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.achievements.services import check_achievements

from .serializers import (
    CustomTokenObtainPairSerializer,
    PasswordChangeSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
)
from .services import build_profile_payload


class AuthThrottleMixin:
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class RegisterView(AuthThrottleMixin, APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        check_achievements(user)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(AuthThrottleMixin, TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class RefreshLoginView(AuthThrottleMixin, TokenRefreshView):
    permission_classes = [AllowAny]


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "'refresh' maydoni kerak."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Token yaroqsiz yoki allaqachon bekor qilingan."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Tizimdan chiqdingiz."}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    def get(self, request):
        payload = build_profile_payload(request.user)
        return Response(payload)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(build_profile_payload(request.user))


class TelegramConnectUrlView(APIView):
    """Bir martalik kod bilan t.me deep-link qaytaradi."""

    def get(self, request):
        import secrets

        user = request.user
        if user.telegram_chat_id:
            return Response({"connected": True})
        code = secrets.token_urlsafe(16)
        user.telegram_link_code = code
        user.save(update_fields=["telegram_link_code"])
        return Response(
            {
                "connected": False,
                "url": f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={code}",
            }
        )


class ChangePasswordView(APIView):
    def patch(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Parol muvaffaqiyatli o'zgartirildi."})
