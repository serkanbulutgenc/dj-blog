from typing import Any
from django.db.models import Model
from ninja_extra import (
    ModelControllerBase,
    ModelConfig,
    api_controller,
    ModelSchemaConfig,    
    route
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
    CategoryListSchema, CategoryDetailSchema, CategoryCreateSchema
)  # , CategoryCreateSchema, CategoryRetrieveSchema
from ninja_extra import ModelService
from ninja_schema import Schema

class NotFoundScheme(Schema):
    message:str|None = None
class ResponseErrorSchema(Schema):
    success:bool = False

class PostModelService(ModelService):
    def create(self, schema: BaseModel, **kwargs: Any) -> Any:
        post_data = schema.model_dump()
        category_id = post_data.pop("categoryId")

        print("post data : ", post_data, kwargs)
        post = self.model._default_manager.create(**post_data, category_id=category_id)

        return post



@api_controller("/posts", tags=["post"], auth=[x_session_token_auth])
class PostModelController(ModelControllerBase):
    service_type = PostModelService
    model_config = ModelConfig(
        model=Post,
        schema_config=ModelSchemaConfig(
            exclude=set(),
            extra_config_dict={
                "title": "PostSchema",
                "description": "Schema for Post model",
            },
        ),
        allowed_routes=["create","list"],#,"find_one" , 'update', 'patch'],
        list_route_info={"by_alias": True},
        create_route_info={"by_alias": True},
        create_schema=PostCreateSchema,
        retrieve_schema=PostListSchema,
    )
    
    @route.get('/{int:post_id}', response=PostListSchema)
    def get_post(self, post_id:int):
        post = get_object_or_404(Post, pk=post_id)
        return post
    
    @route.delete('/{int:post_id}', response={200:DeletePostResponseSchema,404:NotFoundScheme, 400:ResponseErrorSchema})
    def post_delete(self, post_id:int):
        post = get_object_or_404(Post, pk=post_id)
        count ,_ = post.delete()
        if count:
            return 200,{"data":{"id":post_id, "message":"Post deleted"}}
        return 400,{"success":False}
    
    
    
    

@api_controller("/categories", tags=["category"], auth=[x_session_token_auth])
class CategoryModelController(ModelControllerBase):
    model_config = ModelConfig(
        model=Category,
        schema_config=ModelSchemaConfig(
            exclude=set(),
            extra_config_dict={
                "title": "CategorySchema",
                "description": "Schema for Category model",
            }
        ),
        list_route_info={"by_alias": True},
        create_route_info={"by_alias": True},
        create_schema=CategoryCreateSchema,
        retrieve_schema=CategoryListSchema,
    )
