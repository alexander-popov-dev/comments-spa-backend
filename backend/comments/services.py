import io
import logging
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image

logger = logging.getLogger(__name__)


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
