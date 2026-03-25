from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from comments.models import Comment
from comments.permissions import IsOwner
from comments.serializers import CommentSerializer, UpdateCommentSerializer


class CommentViewSet(ModelViewSet):
    """ViewSet for creating, retrieving, updating, deleting and replying to comments."""

    queryset = Comment.objects.all()

    def get_permissions(self):
        """Allow only authenticated owners to update or delete comments."""
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        """Use a restricted serializer for update actions."""
        if self.action in ["update", "partial_update"]:
            return UpdateCommentSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        """Attach authenticated user data on comment creation."""
        user = self.request.user if self.request.user.is_authenticated else None
        extra = {}
        if user:
            extra = {"user": user, "username": user.username, "email": user.email}
        serializer.save(**extra)

    @action(detail=True, methods=["post"])
    def reply(self, request, pk=None):
        """Create a reply to an existing comment."""
        get_object_or_404(Comment, pk=pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user if request.user.is_authenticated else None
        extra = {"parent_comment_id": pk}

        if user:
            extra.update({"user": user, "username": user.username, "email": user.email})
        serializer.save(**extra)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
