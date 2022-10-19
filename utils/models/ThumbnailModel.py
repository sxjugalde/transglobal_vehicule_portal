from django.db import models
from django.utils.html import format_html


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
