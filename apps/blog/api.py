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
    def create(self, schema: BaseModel, **kwargs: Any) -> Any:
        post_data = schema.model_dump()
        category_id = post_data.pop("categoryId")

        post = Post(**post_data, category_id=category_id)
        post.save()

        return post

    # def get_all(self, **kwargs):
    #     print("list", kwargs)
    #     return super().get_all(**kwargs)


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
        ],  # ,"find_one" , 'update', 'patch'],
        list_route_info={"by_alias": True},
        create_route_info={"by_alias": True},
        create_schema=PostCreateSchema,
        retrieve_schema=PostListSchema,
    )

    @route.get("/{int:post_id}", response=PostListSchema)
    def get_post(self, post_id: int):
        post = get_object_or_404(Post, pk=post_id)
        return post

    @route.put("/{int:post_id}", response=PostDetailSchema)
    def put_post(self, schema: PostCreateSchema, post_id: int):
        post = get_object_or_404(Post, pk=post_id)
        post_category = get_object_or_404(Category, pk=schema.category_id)

        for key, value in schema.model_dump().items():
            setattr(post, key, value)
        post.category = post_category
        post.save()
        return post

    @route.delete(
        "/{int:post_id}",
        response={
            200: DeletePostResponseSchema,
            404: NotFoundScheme,
            400: ResponseErrorSchema,
        },
    )
    def post_delete(self, post_id: int):
        post = get_object_or_404(Post, pk=post_id)
        count, _ = post.delete()
        if count:
            return 200, {"data": {"id": post_id, "message": "Post deleted"}}
        return 400, {"success": False}


@api_controller("/categories", tags=["category"],auth=[jwt_token_auth])
class CategoryModelController(ModelControllerBase):
    model_config = ModelConfig(
        model=Category,
        schema_config=ModelSchemaConfig(
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
