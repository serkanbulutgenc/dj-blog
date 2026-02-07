from pydantic import BaseModel, ConfigDict, Field, PositiveInt, AliasGenerator
from pydantic.alias_generators import to_pascal, to_camel, to_snake
from typing import Any
from ninja_schema import ModelSchema
from datetime import datetime
from typing import Annotated
from ninja_schema import ModelSchema, Schema
from .models import Post, Category


class DeleteResponseSchema(Schema):
    data:dict[str,Any]|None = None

class CategoryBaseSchema(Schema):
    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=False,
        validate_by_alias=True,
        serialize_by_alias=True,
        validate_assignment=True,
        alias_generator=AliasGenerator(
            validation_alias=to_snake, serialization_alias=to_camel
        ),
    )

    title: Annotated[str, Field(max=255, description="Category title")]

class CategoryCreateSchema(CategoryBaseSchema):
    pass

class CategoryListSchema(CategoryBaseSchema):
    slug: Annotated[str | None, Field(max=255, description="Category slug")]=None
    id: Annotated[PositiveInt, Field(description="Category Id")]

class CategoryDetailSchema(CategoryListSchema):
    description: Annotated[
        str | None, Field(max=255, description="Category dscription")
    ]    

class PostBaseSchema(Schema):
    model_config = ConfigDict(
        serialize_by_alias=True,
        validate_by_name=True,
        validate_by_alias=True,
        alias_generator=AliasGenerator(
            validation_alias=to_camel, serialization_alias=to_camel
        ),
    )

    title: Annotated[str, Field(max=255, description="Post title")]
    body: Annotated[str, Field(min=25, description="Post body")]

class PostCreateSchema(PostBaseSchema):
    category_id: Annotated[
        PositiveInt|None, Field(description="Post Category", alias="categoryId")]

class PostListSchema(PostCreateSchema):
    category_id:Annotated[
        PositiveInt|None, Field(description="Post Category", alias="categoryId", exclude=True)]=None
    id: Annotated[PositiveInt, Field(description="Post Id")]
    slug: Annotated[str, Field(max="255", description="Post Slug")]
    category: CategoryListSchema

class PostDetailSchema(PostListSchema):
    created_at: datetime
    updated_at:datetime
