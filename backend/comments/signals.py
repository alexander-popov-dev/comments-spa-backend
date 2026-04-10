import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from comments.serializers import CommentSerializer

from .models import Comment
from .tasks import comment_image_resize_task

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


@receiver(post_save, sender=Comment)
def on_comment_saved(sender, instance, created, **kwargs):
    """On save: invalidate cache, queue image resize if needed, broadcast event via WebSocket."""
    cache.delete_pattern("comments_list:*")  # type: ignore[union-attr]

    if created:
        logger.info("New comment created: id=%s", instance.id)

        if instance.image_file:
            comment_image_resize_task.apply_async(kwargs={"comment_id": instance.id})
            logger.info("Image resize task queued for comment %s", instance.id)

    action = "created" if created else "updated"
    async_to_sync(channel_layer.group_send)(
        "comments",
        {
            "type": "comment_event",
            "data": {"action": action, "comment": CommentSerializer(instance).data},
        },
    )


@receiver(post_delete, sender=Comment)
def on_comment_deleted(sender, instance, **kwargs):
    """On delete: invalidate cache and broadcast deleted event with comment id via WebSocket."""
    cache.delete_pattern("comments_list:*")  # type: ignore[union-attr]
    async_to_sync(channel_layer.group_send)(
        "comments",
        {
            "type": "comment_event",
            "data": {"action": "deleted", "id": instance.id},
        },
    )
