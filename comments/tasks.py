from celery import shared_task

from .models import Comment
from .services import CommentService


@shared_task
def comment_image_resize_task(comment_id: int):
    """Resize the image attached to a comment. Silently skips if the comment no longer exists."""
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return

    if comment.image_file:
        resized = CommentService.resize_image(comment.image_file)
        comment.image_file = resized
        comment.save(update_fields=["image_file"])
