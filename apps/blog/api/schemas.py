from __future__ import annotations

from typing import Annotated

from ninja import Field
from ninja import ModelSchema
from ninja.filter_schema import FilterSchema
from pydantic import PositiveInt  # noqa:TC002

from apps.blog.models import Category
from apps.blog.models import Post
from apps.blog.models import Tag


class TagSchemas:
    class TagListSchema(ModelSchema):
        class Meta:
            model = Tag
            fields = ("id", "name", "slug")

    class TagDetailSchema(ModelSchema):
        class Meta:
            model = Tag
            fields = "__all__"

    class TagInSchema(ModelSchema):
        class Meta:
            model = Tag
            fields = ("name",)
            fields_optional = "__all__"

    class TagFilterSchema(FilterSchema):
        name: str | None = None
        slug: str | None = None


class CategoryListSchema(ModelSchema):
    class Meta:
        model = Category
        fields = ("id", "title", "slug")


class CategoryDetailSchema(ModelSchema):
    class Meta:
        model = Category
        fields = "__all__"


class CategoryInSchema(ModelSchema):
    class Meta:
        model = Category
        fields = ("title",)
        fields_optional = "__all__"


class CategoryFilterSchema(FilterSchema):
    title: str | None = None


class PostInSchema(ModelSchema):
    category: Annotated[int | None, "Category ID", Field(alias="category_id")] = None
    tags: list[Annotated[PositiveInt | None, "Tag IDs", Field(max_length=10)]] = None

    class Meta:
        model = Post
        fields = ("title", "content", "category")
        fields_optional = "__all__"


class PostListSchema(ModelSchema):
    category: CategoryListSchema | None = None
    tags: list[TagSchemas.TagListSchema] | None = None
    owner: Annotated[str | None, Field(alias="owner.username")]

    class Meta:
        model = Post
        fields = ("id", "title", "slug")


class PostOutSchema(ModelSchema):
    class Meta:
        model = Post
        fields = ("id", "title")


class PostDetailSchema(ModelSchema):
    class Meta:
        model = Post
        fields = "__all__"


class PostFilterSchema(FilterSchema):
    title: str | None = None
    content: str | None = None
