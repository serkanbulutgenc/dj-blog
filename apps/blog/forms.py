from django import forms

from .models import Post


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "category", "content")
