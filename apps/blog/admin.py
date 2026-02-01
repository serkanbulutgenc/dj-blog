from django.contrib import admin
from .models import Post, Category
from django.utils.text import slugify


# Register your models here.,
@admin.register(Post)
class PostModelAdmin(admin.ModelAdmin):
    list_display = ["title", "category"]

    def save_form():
        pass

    def save_model(self, request, instance, form, change):
        instance.slug = slugify(form.cleaned_data.get("title"), allow_unicode=False)
        super().save_model(request, instance, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title"]

    def save_model(self, request, instance, form, change):
        instance.slug = slugify(form.cleaned_data.get("title"), allow_unicode=False)
        super().save_model(request, instance, form, change)
