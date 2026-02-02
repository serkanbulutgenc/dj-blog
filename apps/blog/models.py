from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    title = models.CharField(_("Title"), max_length=255, help_text=_("Category title"))
    slug = models.SlugField(
        _("Slug"),
        max_length=255,
        help_text=_("Slug"),
        editable=False,
        unique=True,
        null=False,
        blank=True,
    )
    description = models.TextField(
        _("Description"), max_length=255, help_text=_("Category Description")
    )
    created_at = models.DateTimeField(_("Created"), auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(_("Updated"), auto_now=True, editable=False)

    def save(self, **kwargs):
        self.slug = slugify(self.title, allow_unicode=False)
        super().save(**kwargs)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("Category_detail", kwargs={"pk": self.pk})


# Create your models here.
class Post(models.Model):
    title = models.CharField(_("Title"), max_length=255, help_text=_("Post title"))
    slug = models.SlugField(
        _("Slıg"),
        max_length=255,
        help_text=_("Slug"),
        unique=True,
        editable=False,
        null=False,
        blank=True,
    )
    category = models.ForeignKey(
        "Category",
        verbose_name=_("Category"),
        on_delete=models.CASCADE,
        related_name="posts",
    )
    body = models.TextField(_("Body"), help_text=_("Post Body"))
    created_at = models.DateTimeField(_("Created"), auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(_("Updated"), auto_now=True, editable=False)

    def save(self, **kwargs):
        self.slug = slugify(self.title, allow_unicode=False)
        super().save(**kwargs)

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})
