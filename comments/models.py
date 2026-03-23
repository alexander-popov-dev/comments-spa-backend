from django.conf import settings
from django.db import models


class Comment(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    homepage = models.URLField(blank=True)
    comment = models.TextField()
    text_file = models.FileField(upload_to="comments/text_file", null=True, blank=True)
    image_file = models.ImageField(upload_to="comments/image_file", null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "comment"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
