from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Post(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
        help_text=_("Enter the title of the post"),
        validators=[MinLengthValidator(5)],
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        editable=False,
        verbose_name=_("Slug"),
    )
    content = models.TextField(
        verbose_name=_("Content"),
        max_length=1000,
        help_text=_("Enter the content of the post"),
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["slug"], name="unique_slug")]

    def __str__(self):
        return self.title
