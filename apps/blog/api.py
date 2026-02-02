from typing import Any, Annotated
from django.db.models import Model, Q
from ninja_extra import (
    ModelControllerBase,
    ModelConfig,
    api_controller,
    ModelSchemaConfig,
    route,
)
from django.shortcuts import get_object_or_404
from allauth.headless.contrib.ninja.security import jwt_token_auth, x_session_token_auth
from allauth.headless.adapter import DefaultHeadlessAdapter
from pydantic import BaseModel
from .models import Post, Category
from .schemas import (
    PostListSchema,
    PostDetailSchema,
    PostCreateSchema,
    DeletePostResponseSchema,
    CategoryListSchema,
    CategoryDetailSchema,
    CategoryCreateSchema,
)  # , CategoryCreateSchema, CategoryRetrieveSchema
from ninja_extra import ModelService, ModelPagination
from ninja_extra.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    PageNumberPaginationExtra,
)
from ninja_schema import Schema
from ninja import FilterSchema, FilterLookup
# from allauth.headless.tokens.strategies.jwt.strategy import JWTTokenStrategy


class NotFoundScheme(Schema):
    message: str | None = None


class ResponseErrorSchema(Schema):
    success: bool = False


# Define a FilterSchema for your model
class PostFilterSchema(FilterSchema):
    title: Annotated[str | None, FilterLookup("title__icontains")] = None
    category: Annotated[str | None, FilterLookup("category__title__iexact")] = None
    ids: str | None = None

    def filter_ids(self, value: str) -> Q:
        ids = value.split(",") if value else []
        return Q(id__in=ids)


class PostModelService(ModelService):
    def create(self, schema: BaseModel, **kwargs: Any) -> PostCreateSchema:
        post_data = schema.model_dump()
        category_id = post_data.pop("categoryId")

        post = Post(**post_data, category_id=category_id)
        post.save()

        return post

    def update(self, instance, schema, **kwargs) -> PostDetailSchema:
        post_category = get_object_or_404(Category, pk=schema.category_id)

        for key, value in schema.model_dump().items():
            setattr(instance, key, value)
        instance.category = post_category
        instance.save()
        return instance


@api_controller("/posts", tags=["post"], auth=[jwt_token_auth])
class PostModelController(ModelControllerBase):
    service_type = PostModelService
    model_config = ModelConfig(
        model=Post,
        pagination=ModelPagination(
            klass=PageNumberPaginationExtra, filter_schema=PostFilterSchema
        ),
        schema_config=ModelSchemaConfig(
            exclude=set(),
            extra_config_dict={
                "title": "PostSchema",
                "description": "Schema for Post model",
            },
        ),
        allowed_routes=[
            "create",
            "list",
            "delete",
            "find_one",
            "update",
        ],  # "find_one","update","patch",,"find_one" , 'update', 'patch'],
        list_route_info={"by_alias": True},
        create_route_info={"by_alias": True},
        create_schema=PostCreateSchema,
        retrieve_schema=PostListSchema,
    )


@api_controller("/categories", tags=["category"], auth=[jwt_token_auth])
class CategoryModelController(ModelControllerBase):
    model_config = ModelConfig(
        model=Category,
        schema_config=ModelSchemaConfig(
            read_only_fields=["id", "created_at", "updated_at"],
            exclude=set(),
            extra_config_dict={
                "title": "CategorySchema",
                "description": "Schema for Category model",
            },
        ),
        list_route_info={"by_alias": True},
        create_route_info={"by_alias": True},
        create_schema=CategoryCreateSchema,
        retrieve_schema=CategoryListSchema,
    )
