import logging

from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import TokenError as JWTTokenError
from rest_framework_simplejwt.tokens import RefreshToken

from users.auth.base import BaseAuth
from users.dto import JWTAuthResponse
from users.exceptions import AuthenticationError, InvalidTokenError
from users.models import User

logger = logging.getLogger(__name__)


class JWTAuth(BaseAuth):
    """JWT-based authentication backend."""

    def register(self, validated_data: dict) -> JWTAuthResponse:
        """Create a new user and return JWT tokens."""
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        logger.info("New user registered: %s", user.email)
        return self._make_tokens(user)

    def login(self, email: str, password: str) -> JWTAuthResponse:
        """Authenticate user and return JWT tokens."""
        user = authenticate(email=email, password=password)
        if not user:
            logger.warning("Failed login attempt for email: %s", email)
            raise AuthenticationError("Invalid email or password")
        logger.info("User logged in: %s", user.email)
        return self._make_tokens(user)

    def logout(self, credential: str) -> None:
        """Blacklist the given refresh token."""
        try:
            token = RefreshToken(credential)
            token.blacklist()
            logger.info("User logged out, token blacklisted")
        except JWTTokenError:
            raise InvalidTokenError("Invalid token")

    def _make_tokens(self, user: User) -> JWTAuthResponse:
        """Generate access and refresh tokens for the given user."""
        refresh = RefreshToken.for_user(user)
        return JWTAuthResponse(
            username=user.username,
            email=user.email,
            access=str(refresh.access_token),
            refresh=str(refresh),
        )
