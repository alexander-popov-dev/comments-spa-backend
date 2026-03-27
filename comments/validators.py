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
