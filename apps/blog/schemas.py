# from pydantic import BaseModel, ConfigDict, Field, PositiveInt, AliasGenerator
# from pydantic.alias_generators import to_pascal, to_camel, to_snake
from typing import Any
from datetime import datetime
from typing import Annotated
from .models import Post, Category

from msgspec import Struct, Meta
from django_bolt.serializers import (
    Serializer,
    PositiveInt,
    Slug200,
    Char255,
    Slug,
    Meta,
    Text,
    Nested,
)


class FilterParams(Struct):
    page: int = 1
    page_size: int = 10
    sort_by: str | None = None


class DeleteResponse(Struct):
    data: dict[str, Any]


class CategorySerializer(Serializer, rename="camel"):
    id: PositiveInt
    title: Char255
    slug: Slug200
    description: Text | None
    created_at: datetime
    updated_at: datetime

    class Config:
        readonly_fields = ["created_at", "updated_at", "slug"]
        field_sets = {
            "list": ["id", "title", "slug"],
            "detail": ["id", "title", "slug", "description"],
            "create": ["title", "description"],
        }


CategoryListSerializer = CategorySerializer.fields("list")
CategoryDetailSerializer = CategorySerializer.fields("detail")
CategoryCreateSerializer = CategorySerializer.fields("create")


class PostSerializer(Serializer, rename="camel"):
    id: PositiveInt
    title: Char255
    slug: Slug200
    category: Annotated[CategoryListSerializer, Nested(CategoryListSerializer)]
    category_id: int
    body: Text | None
    created_at: datetime
    updated_at: datetime

    class Config:
        read_only_fields = [
            "slug",
            "created_at",
            "updated_at",
        ]
        write_only = {"category_id"}
        field_sets = {
            "list": ["id", "title", "slug", "category"],
            "detail": ["id", "title", "body", "category", "created_at", "updated_at"],
            "create": ["title", "body", "category_id"],
        }


PostListSerializer = PostSerializer.fields("list")
PostDetailSerializer = PostSerializer.fields("detail")
PostCreateSerializer = PostSerializer.subset("title", "body", "category_id")
