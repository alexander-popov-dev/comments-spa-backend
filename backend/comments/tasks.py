import logging
from pathlib import Path

from celery import shared_task

from .models import Comment
from .services import CommentService

logger = logging.getLogger(__name__)


@shared_task
def comment_image_resize_task(comment_id: int):
    """Resize the image attached to a comment. Silently skips if the comment no longer exists."""
    logger.info("Image resize task started for comment %s", comment_id)

    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        logger.warning("Comment %s not found, skipping image resize", comment_id)
        return

    if comment.image_file:
        resized = CommentService.resize_image(comment.image_file)
        original_name = Path(comment.image_file.name).name
        comment.image_file.delete(save=False)
        comment.image_file.save(original_name, resized, save=False)
        comment.save(update_fields=["image_file"])
        logger.info("Image resize task completed for comment %s", comment_id)
