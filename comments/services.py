import io

from django.core.files.base import ContentFile
from PIL import Image


class CommentService:
    @staticmethod
    def resize_image(image, max_width=320, max_height=240):
        """Resize image to fit within max_width x max_height. Returns the original if already within bounds."""
        img = Image.open(image)
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height))
            output = io.BytesIO()
            fmt = img.format or "JPEG"
            img.save(output, format=fmt)
            output.seek(0)
            return ContentFile(output.read(), name=image.name)
        return image
