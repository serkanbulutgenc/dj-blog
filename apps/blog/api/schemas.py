from ninja import ModelSchema
from ninja.filter_schema import FilterSchema

from apps.blog.models import Post


class PostInSchema(ModelSchema):
    class Meta:
        model = Post
        fields = ("title", "content")
        fields_optional = "__all__"


class PostListSchema(ModelSchema):
    class Meta:
        model = Post
        fields = ("id", "title", "slug")


class PostDetailSchema(ModelSchema):
    class Meta:
        model = Post
        fields = "__all__"


class PostFilterSchema(FilterSchema):
    title: str | None = None
    content: str | None = None
