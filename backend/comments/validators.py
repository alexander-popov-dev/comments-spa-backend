from pathlib import Path

import bleach
from django.conf import settings
from lxml import etree
from rest_framework import serializers


def validate_html_tags(value: str) -> str:
    """Allows only whitelisted HTML tags."""

    cleaned = bleach.clean(
        value,
        tags=settings.COMMENT_ALLOWED_HTML_TAGS,
        attributes=settings.COMMENT_ALLOWED_HTML_ATTRIBUTES,
        strip=True,
    )

    if cleaned != value:
        raise serializers.ValidationError(
            f"Text contains forbidden HTML tags. Allowed: {settings.COMMENT_ALLOWED_HTML_TAGS}."
        )

    return value


def validate_xhtml_structure(value: str) -> None:
    """Checks that all HTML tags are properly closed (XHTML validation)."""

    try:
        etree.fromstring(f"<root>{value}</root>")

    except etree.XMLSyntaxError as e:
        raise serializers.ValidationError(f"Invalid XHTML: {e.msg}. Make sure all tags are properly closed and nested.")


def validate_image_file_format(image_file) -> None:
    """Validates that the uploaded image has an allowed format (JPG, GIF, PNG)."""

    if not image_file:
        return

    extension = Path(image_file.name).suffix.lstrip(".").lower()

    if extension not in ["jpg", "jpeg", "gif", "png"]:
        raise serializers.ValidationError("Invalid image file format. Allowed: JPG, GIF, PNG.")


def validate_text_file_size(text_file) -> None:
    """Validates text file format and size."""

    if not text_file:
        return

    extension = Path(text_file.name).suffix.lstrip(".").lower()

    if extension != "txt":
        raise serializers.ValidationError("Invalid text file format. Allowed: TXT.")

    if text_file.size > 100 * 1024:
        raise serializers.ValidationError("Text file size must not exceed 100 KB.")
