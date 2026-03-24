from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Custom user model. Uses email as the primary identifier."""

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, validators=[RegexValidator(r"^[a-zA-Z0-9]+$")])
    homepage = models.URLField(blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "user"

    def __str__(self):
        return self.email
