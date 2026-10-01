from django.contrib import admin

from .forms import PostAdminForm
from .models import Category
from .models import Post
from .models import Tag


# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created")
    form = PostAdminForm
    """
    def save_model(self, request, obj, form, change):
        post_slug = slugify(form.cleaned_data.get("title"))

        if Post.objects.filter(slug=post_slug).exists() and not change:
            post_slug = f"{post_slug}-{uuid1().hex[:6]}"
        obj.slug = post_slug

        super().save_model(request, obj, form, change)
    """


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created")
