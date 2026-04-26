from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, RegisterSerializer


def _tokens_for_user(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "username": user.username,
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    Validate username/password against Django users; return JWT pair on success.
    """
    ser = LoginSerializer(data=request.data)
    if not ser.is_valid():
        return Response(
            {"detail": "Username and password are required.", "errors": ser.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    username = ser.validated_data["username"]
    password = ser.validated_data["password"]

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {"detail": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    if not user.is_active:
        return Response(
            {"detail": "This account is disabled."},
            status=status.HTTP_403_FORBIDDEN,
        )

    return Response(_tokens_for_user(user), status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    """
    Create a new Django user (hashed password) and return JWT pair.
    """
    ser = RegisterSerializer(data=request.data)
    if not ser.is_valid():
        return Response(
            {"detail": "Invalid registration data.", "errors": ser.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    username = ser.validated_data["username"]
    password = ser.validated_data["password"]
    email = (ser.validated_data.get("email") or "").strip()
    full_name = (ser.validated_data.get("full_name") or "").strip()

    if User.objects.filter(username__iexact=username).exists():
        return Response(
            {"detail": "That username is already taken."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_password(password, user=User(username=username))
    except DjangoValidationError as exc:
        return Response(
            {"detail": " ".join(exc.messages)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=full_name[:150] if full_name else "",
    )
    return Response(_tokens_for_user(user), status=status.HTTP_201_CREATED)
