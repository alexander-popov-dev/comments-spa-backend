from django.core.validators import RegexValidator
from rest_framework import serializers

from comments.models import Comment
from comments.validators import validate_html_tags, validate_xhtml_structure


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for creating and retrieving comments."""

    username = serializers.CharField(
        min_length=2,
        max_length=150,
        validators=[RegexValidator(regex=r"^[a-zA-Z0-9]+$", message="Username must contain only letters and numbers.")],
    )

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

    def validate_comment(self, value):
        validate_xhtml_structure(value=value)
        return validate_html_tags(value=value)


class CommentDetailSerializer(serializers.ModelSerializer):
    """Serializer for retrieving a single comment with full reply tree."""

    replies = serializers.SerializerMethodField()

    def get_replies(self, obj):
        return CommentDetailSerializer(obj.replies.order_by("created_at").all(), many=True).data

    class Meta:
        model = Comment
        fields = ["id", "user", "username", "email", "comment", "created_at", "updated_at", "replies"]


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

    def validate_comment(self, value):
        validate_xhtml_structure(value=value)
        return validate_html_tags(value=value)
