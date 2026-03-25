from rest_framework import serializers

from comments.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for creating and retrieving comments."""

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "parent_comment",
            "username",
            "email",
            "homepage",
            "comment",
            "text_file",
            "image_file",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "user": {"read_only": True},
            "parent_comment": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def validate(self, attrs):
        """Require username and email for anonymous users."""
        request = self.context["request"]
        if not request.user.is_authenticated:
            if not attrs.get("username"):
                raise serializers.ValidationError({"username": "This field is required."})
            if not attrs.get("email"):
                raise serializers.ValidationError({"email": "This field is required."})
        return attrs


class UpdateCommentSerializer(serializers.ModelSerializer):
    """Serializer for updating comment text only."""

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "parent_comment",
            "comment",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "user": {"read_only": True},
            "parent_comment": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }
