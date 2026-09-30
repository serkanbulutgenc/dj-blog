from uuid import uuid1

from django.contrib import admin
from django.utils.text import slugify

from .forms import PostAdminForm
from .models import Post


# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created_at")
    form = PostAdminForm

    def save_model(self, request, obj, form, change):
        post_slug = slugify(form.cleaned_data.get("title"))

        if Post.objects.filter(slug=post_slug).exists() and not change:
            post_slug = f"{post_slug}-{uuid1().hex[:6]}"
        obj.slug = post_slug

        super().save_model(request, obj, form, change)
