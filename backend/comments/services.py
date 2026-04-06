import io
import logging
from pathlib import Path

from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.core.files.base import ContentFile
from PIL import Image
from rest_framework import serializers

logger = logging.getLogger(__name__)


class CaptchaService:
    """Service for generating and validating CAPTCHA challenges."""

    @staticmethod
    def generate() -> dict:
        """Generate a new CAPTCHA and return its key and image URL."""
        key = CaptchaStore.generate_key()
        return {"key": key, "image_url": captcha_image_url(key)}

    @staticmethod
    def validate(key: str | None, value: str | None) -> None:
        """Validate the given CAPTCHA key/value pair. Raises ValidationError on failure."""
        if not key or not value:
            raise serializers.ValidationError({"captcha": "Captcha is required."})
        try:
            captcha = CaptchaStore.objects.get(hashkey=key)
            if captcha.response != value.lower().strip():
                raise serializers.ValidationError({"captcha": "Invalid captcha."})
            captcha.delete()
        except CaptchaStore.DoesNotExist:
            raise serializers.ValidationError({"captcha": "Invalid captcha."})


class CommentService:
    @staticmethod
    def resize_image(image, max_width=320, max_height=240):
        """Resize image to fit within max_width x max_height. Returns the original if already within bounds."""
        img = Image.open(image)
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height))
            logger.info("Image %s resized to %sx%s", image.name, img.width, img.height)
            output = io.BytesIO()
            fmt = img.format or "JPEG"
            img.save(output, format=fmt)
            output.seek(0)
            return ContentFile(output.read(), name=Path(image.name).name)
        logger.debug("Image %s is within bounds (%sx%s), skipping resize", image.name, img.width, img.height)
        return image
