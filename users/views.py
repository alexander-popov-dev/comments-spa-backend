from rest_framework import generics, permissions, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

from .auth.jwt import JWTAuth
from .exceptions import AuthenticationError, InvalidTokenError
from .serializers import LoginSerializer, LogoutSerializer, RegisterSerializer


class RegisterView(generics.GenericAPIView):
    """Register a new user and return JWT tokens."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth = JWTAuth()
        data = auth.register(validated_data=serializer.validated_data)
        return Response(data=data.to_dict(), status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """Authenticate user and return JWT tokens."""

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth = JWTAuth()

        try:
            data = auth.login(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
        except AuthenticationError as e:
            raise AuthenticationFailed(str(e))

        return Response(data=data.to_dict(), status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    """Blacklist refresh token to log out the user."""

    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth = JWTAuth()

        try:
            auth.logout(credential=serializer.validated_data["refresh"])
        except InvalidTokenError as e:
            raise AuthenticationFailed(str(e))

        return Response(status=status.HTTP_204_NO_CONTENT)
