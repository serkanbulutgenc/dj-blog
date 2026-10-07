# Create your models here.
import logging

from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import AutoSlugField
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.models import TitleSlugDescriptionModel

logger = logging.getLogger(__name__)

USER_MODEL = get_user_model()


class Category(TitleSlugDescriptionModel, TimeStampedModel, models.Model):
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["-created"]
        constraints = [
            models.UniqueConstraint(fields=["slug"], name="unique_category_slug"),
        ]

    def __str__(self):
        return self.title


class Tag(TimeStampedModel, models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("Enter the name of the tag"),
        validators=[MinLengthValidator(3)],
    )
    slug = AutoSlugField(
        populate_from="name",
        unique=True,
        blank=True,
        editable=False,
        overwrite=True,
        verbose_name=_("Slug"),
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["-created"]
        constraints = [
            models.UniqueConstraint(fields=["slug"], name="unique_tag_slug"),
        ]

    def __str__(self):
        return self.name


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
    owner = models.ForeignKey(
        USER_MODEL,
        default=None,
        null=False,
        editable=False,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name=_("Owner"),
        help_text=_("Select the owner of the post"),
    )
    category = models.ForeignKey(
        Category,
        default=None,
        null=True,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name=_("Category"),
        help_text=_("Select the category of the post"),
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="posts",
        verbose_name=_("Tags"),
        help_text=_("Select the tags for the post"),
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
        constraints = [
            models.UniqueConstraint(fields=["slug"], name="unique_post_slug"),
        ]

    def __str__(self):
        return self.title
