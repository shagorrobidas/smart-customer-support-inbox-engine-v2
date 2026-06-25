from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """
    Abstract base model with common fields
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    is_active = models.BooleanField(
        default=True
    )

    deleted_at = models.DateTimeField(
        null=True, blank=True
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])
