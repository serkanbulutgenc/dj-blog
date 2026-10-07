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

    def save_model(self, request, obj, form, change):
        if not obj.owner_id:
            obj.owner = request.user
        else:
            obj.owner = request.user
        obj.save()

        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        if request.user.is_superuser:
            qs = super().get_queryset(request)
        else:
            qs = super().get_queryset(request).filter(owner=request.user)
        return qs


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created")
