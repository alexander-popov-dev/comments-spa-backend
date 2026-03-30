from django.core.validators import RegexValidator
from rest_framework import serializers

from comments.models import Comment
from comments.validators import (
    validate_html_tags,
    validate_image_file_format,
    validate_text_file_size,
    validate_xhtml_structure,
)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for creating and listing comments."""

    username = serializers.CharField(
        required=False,
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
        """Require username and email for anonymous users.
        Disallow attaching both image and text file simultaneously."""

        request = self.context.get("request")

        if request and not request.user.is_authenticated:
            if not attrs.get("username"):
                raise serializers.ValidationError({"username": "This field is required."})

            if not attrs.get("email"):
                raise serializers.ValidationError({"email": "This field is required."})

        if attrs.get("image_file") and attrs.get("text_file"):
            raise serializers.ValidationError("You can attach either an image or a text file, not both.")

        return attrs

    def validate_comment(self, value):
        """Validate XHTML structure and allowed HTML tags."""
        validate_xhtml_structure(value=value)
        return validate_html_tags(value=value)

    def validate_image_file(self, value):
        """Validate image file format (JPG, GIF, PNG)."""
        validate_image_file_format(image_file=value)
        return value

    def validate_text_file(self, value):
        """Validate text file format (TXT) and size (max 100 KB)."""
        validate_text_file_size(text_file=value)
        return value


class CommentDetailSerializer(serializers.ModelSerializer):
    """Serializer for retrieving a single comment with full reply tree."""

    replies = serializers.SerializerMethodField()

    def get_replies(self, obj):
        """Return recursively serialized replies ordered by creation date."""
        return CommentDetailSerializer(
            obj.replies.prefetch_related("replies").order_by("created_at").all(), many=True
        ).data

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "username",
            "email",
            "comment",
            "text_file",
            "image_file",
            "created_at",
            "updated_at",
            "replies",
        ]


class UpdateCommentSerializer(serializers.ModelSerializer):
    """Serializer for updating comment text only."""

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "comment",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "user": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def validate_comment(self, value):
        """Validate XHTML structure and allowed HTML tags."""
        validate_xhtml_structure(value=value)
        return validate_html_tags(value=value)
