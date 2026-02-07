from typing import Any, Annotated
from django.db.models import Model, Q
from ninja_extra import (
    ControllerBase,
    ModelControllerBase,
    ModelConfig,
    api_controller,
    http_delete,
    ModelSchemaConfig,
    ModelEndpointFactory,
    route,
)
from django.shortcuts import get_object_or_404
from allauth.headless.contrib.ninja.security import jwt_token_auth, x_session_token_auth
from pydantic import BaseModel
from .models import Post, Category
from .schemas import (
    PostListSchema,
    PostDetailSchema,
    PostCreateSchema,
    DeleteResponseSchema,
    CategoryListSchema,
    CategoryDetailSchema,
    CategoryCreateSchema,
)  # , CategoryCreateSchema, CategoryRetrieveSchema
from ninja_extra import ModelService, ModelPagination
from ninja_extra.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    PageNumberPaginationExtra,
    PaginatedResponseSchema,
    NinjaPaginationResponseSchema,
    paginate
)
from ninja.security import django_auth
from ninja_schema import Schema
from ninja import FilterSchema, FilterLookup
from ninja_extra import status, schemas
# from allauth.headless.tokens.strategies.jwt.strategy import JWTTokenStrategy


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
    
    def delete(self, instance: Model, **kwargs: Any) -> Any:
        print("delete",instance, kwargs)
        instance.delete()
        return {"success":True}

@api_controller('/posts', auth=[x_session_token_auth], tags=['post'])
class PostController(ControllerBase):
    @route.get('/', response=PaginatedResponseSchema[PostListSchema])
    @paginate(PageNumberPaginationExtra,filter_schema=PostFilterSchema,page_size=25)
    def get_posts(self):
        return Post.objects.all()
    
    @route.get('/{int:post_id}', response=PostDetailSchema)
    def get_post(self, post_id:int):
        post = get_object_or_404(Post, pk=post_id)
        return post
    
    @route.post('/', response={201:PostDetailSchema})
    def create_post(self, data:PostCreateSchema):
        post_data = data.model_dump()
        category_id = post_data.pop("categoryId")

        post = Post(**post_data, category_id=category_id)
        post.save()

        return post
    
    @route.generic('/{int:post_id}', methods=['put', 'patch'], response={200:PostDetailSchema})
    def update_post(self, data:PostCreateSchema, post_id:int):
        post = get_object_or_404(Post, pk=post_id)
        post_category = get_object_or_404(Category, pk=data.category_id)
         
        for key, value in data.model_dump().items():
             setattr(post, key, value)
        
        post.category = post_category
        post.save()
        return post
    
    @route.delete('/{int:post_id}', response={200:DeleteResponseSchema})
    def delete_post(self, post_id:int):
        post = get_object_or_404(Post, pk=post_id)
        post.delete()
        return {"data":{"id":post_id, "message":"Post Deleted"}}



'''
@api_controller("/posts", tags=["post"])
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
            #"delete",
            "find_one",
            "update",
        ],  # "find_one","update","patch",,"find_one" , 'update', 'patch'],
        list_route_info={"by_alias": True},
        create_route_info={"by_alias": True},
        delete_route_info={"by_alias":True, "summary":"Delety"},
        create_schema=PostCreateSchema,
        retrieve_schema=PostListSchema,
    )
    def foo(self):
        self.create_response("Foo",200)

    delete_by_id = ModelEndpointFactory.delete(
        path="/{int:id}",
        lookup_param="id",
        status_code=status.HTTP_200_OK,
        response={200:DeleteResponseSchema},
        description='Delete a post',
        summary='Delete a post by ID',
        custom_handler=lambda self, **kwargs:self.create_response("Doo",200)

    )
'''

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


@api_controller('/foo',auth=[x_session_token_auth])
class FooController(ControllerBase):
    @http_delete('/{int:foo_id}',response={200:DeleteResponseSchema})
    def foo_delete(self, foo_id:int):
        print('Foo deleted')
        return {"success":True}