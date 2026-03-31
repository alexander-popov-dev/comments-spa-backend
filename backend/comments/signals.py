import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from comments.serializers import CommentSerializer

from .models import Comment
from .tasks import comment_image_resize_task

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


@receiver(post_save, sender=Comment)
def on_comment_created(sender, instance, created, **kwargs):
    """On new comment: invalidate the comments list cache and trigger async image processing if needed."""
    if created:
        logger.info("New comment created: id=%s", instance.id)
        cache.delete("comments_list")
        if instance.image_file:
            comment_image_resize_task.apply_async(kwargs={"comment_id": instance.id})
            logger.info("Image resize task queued for comment %s", instance.id)
        async_to_sync(channel_layer.group_send)(
            "comments", {"type": "new_comment", "data": CommentSerializer(instance).data}
        )
