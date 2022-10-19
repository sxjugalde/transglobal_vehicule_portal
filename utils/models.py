from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html


# Auditable models
class AuditableModel(models.Model):
    """Sets audit fields, such as created/updated dates and user."""

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_createdby",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_modifiedby",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True


# Soft deletion models
class SoftDeletionQuerySet(models.query.QuerySet):
    "QuerySet used by soft deletion model."

    def delete(self):
        return super(SoftDeletionQuerySet, self).update(deleted_at=timezone.now())

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)


class SoftDeletionManager(models.Manager):
    "Manager used by soft deletion model to fetch appropiate query sets."

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop("alive_only", True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted_at=None)
        return SoftDeletionQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class SoftDeletionModel(models.Model):
    "Abstract model that enables soft-deletion mechanisms."

    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()


# Thumbnail model
class ThumbnailModel(models.Model):
    "Abstract model with thumbnail image upload and reference for admin site."

    thumbnail = models.ImageField(blank=True, null=True, upload_to="images/")

    # Show the media files in the list display in the admin panel:
    def image_tag(self):
        if self.thumbnail:
            return format_html(
                '<img href="{0}" src="{0}" height="75" />'.format(self.thumbnail.url)
            )

    image_tag.allow_tags = True
    image_tag.short_description = "Thumbnail"

    class Meta:
        abstract = True
