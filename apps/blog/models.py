# Create your models here.
import logging

from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import AutoSlugField
from django_extensions.db.models import TimeStampedModel

logger = logging.getLogger(__name__)


class Post(TimeStampedModel, models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
        help_text=_("Enter the title of the post"),
        validators=[MinLengthValidator(5)],
    )
    slug = AutoSlugField(
        populate_from="title",
        unique=True,
        blank=True,
        editable=False,
        overwrite=True,
        verbose_name=_("Slug"),
    )
    content = models.TextField(
        verbose_name=_("Content"),
        max_length=1000,
        help_text=_("Enter the content of the post"),
    )

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ["-created"]
        constraints = [models.UniqueConstraint(fields=["slug"], name="unique_slug")]

    def __str__(self):
        return self.title
