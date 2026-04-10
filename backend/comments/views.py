import logging

from django.core.cache import cache
from django.db.models import Count
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from comments.models import Comment
from comments.permissions import IsOwner
from comments.serializers import (
    CommentDetailSerializer,
    CommentPreviewSerializer,
    CommentSerializer,
    UpdateCommentSerializer,
)
from comments.services import CaptchaService

COMMENTS_LIST_CACHE_TIMEOUT = 60 * 30  # 30 minutes

logger = logging.getLogger(__name__)


class CommentViewSet(ModelViewSet):
    """ViewSet for creating, retrieving, updating, deleting and replying to comments."""

    filter_backends = [OrderingFilter]
    ordering_fields = ["username", "email", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return top-level comments with reply count for list, all comments otherwise."""
        if self.action == "list":
            return Comment.objects.filter(parent_comment=None).annotate(replies_count=Count("replies"))

        return Comment.objects.all()

    def list(self, request, *args, **kwargs):
        """Return paginated comments list, served from cache when available."""
        ordering = request.query_params.get("ordering", "-created_at")
        page = request.query_params.get("page", "1")
        cache_key = f"comments_list:{ordering}:{page}"

        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=COMMENTS_LIST_CACHE_TIMEOUT)
        return response

    def get_permissions(self):
        """Allow only authenticated owners to update or delete comments."""
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwner()]

        return [permissions.AllowAny()]

    def get_serializer_class(self):
        """Use a restricted serializer for update actions."""
        if self.action in ["update", "partial_update"]:
            return UpdateCommentSerializer

        if self.action == "retrieve":
            return CommentDetailSerializer

        return CommentSerializer

    def perform_create(self, serializer):
        """Attach authenticated user data on comment creation."""
        user_data = self._attach_user(user=self.request.user)
        comment = serializer.save(**user_data)
        logger.info("Comment created: id=%s by %s", comment.id, self._user_label())

    def perform_update(self, serializer):
        """Log comment update."""
        comment = serializer.save()
        logger.info("Comment updated: id=%s by %s", comment.id, self._user_label())

    def perform_destroy(self, instance):
        """Log comment deletion."""
        logger.info("Comment deleted: id=%s by %s", instance.id, self._user_label())
        instance.delete()

    @action(detail=True, methods=["post"])
    def reply(self, request, pk=None):
        """Create a reply to an existing comment."""
        get_object_or_404(Comment, pk=pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = self._attach_user(user=self.request.user)
        reply = serializer.save(parent_comment_id=pk, **user_data)
        logger.info("Reply created: id=%s for comment %s by %s", reply.id, pk, self._user_label())

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def preview(self, request):
        """Validate and return sanitized comment HTML for preview without saving."""
        serializer = CommentPreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logger.debug("Comment preview requested by %s", self._user_label())

        return Response({"comment": serializer.validated_data["comment"]})

    def _attach_user(self, user):
        """Return user fields dict if authenticated, empty dict otherwise."""
        if user and user.is_authenticated:
            return {"user": user, "username": user.username, "email": user.email}

        return {}

    def _user_label(self) -> str:
        """Return a loggable user identifier."""
        user = self.request.user
        return user.email if user.is_authenticated else "anonymous"


class CaptchaView(APIView):
    """Generate and return a new CAPTCHA key and image URL."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(CaptchaService.generate())
