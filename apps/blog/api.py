from django.shortcuts import get_object_or_404

# from allauth.headless.contrib.ninja.security import jwt_token_auth, x_session_token_auth
from .models import Post, Category
from django_bolt import BoltAPI
from django_bolt.views import ModelViewSet, ViewSet
from django_bolt.params import Body, Path, Query
from django_bolt.exceptions import (
    NotFound,
    UnprocessableEntity,
    ValidationException,
    BadRequest,
)
from django_bolt.responses import JSON
from django_bolt.pagination import PageNumberPagination, paginate, PaginatedResponse
from msgspec import Struct
from django.db import IntegrityError
from django_bolt.request import Request
from typing import Annotated, Any, List
from .schemas import (
    PostListSerializer,
    PostCreateSerializer,
    PostDetailSerializer,
    CategoryListSerializer,
    CategoryCreateSerializer,
    CategoryDetailSerializer,
    FilterParams,
    DeleteResponse,
)


# Define a FilterSchema for your model
post_api = BoltAPI(
    prefix="/", trailing_slash="append", openapi_config={"summary": "Post endpoint"}
)

category_api = BoltAPI(prefix="/", trailing_slash="append")


class CustomPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


@post_api.viewset("", tags=["Posts"])
class PostViewSet(ViewSet):
    queryset = Post.objects.select_related("category")
    serializer_class = PostDetailSerializer

    @paginate(CustomPagination)
    async def list(self, request: Request) -> PaginatedResponse:
        """Gets all post."""
        qs = await self.get_queryset()

        return [PostListSerializer.from_model(post) async for post in qs]

    async def retrieve(self, request, pk: int) -> PostDetailSerializer:
        """Get single post"""
        post = await Post.objects.select_related("category").aget(pk=pk)
        return PostDetailSerializer.from_model(post)

    async def destroy(self, request, pk: int) -> DeleteResponse:
        """
        Delete a post

        Deletes a post according to the ID and returns success status with message.
        """
        post = await Post.objects.aget(pk=pk)
        await post.adelete()
        return JSON(
            {"data": {"id": pk, "message": "Post Deleted"}},
            status_code=200,
        )

    async def create(self, request, data: PostCreateSerializer) -> PostDetailSerializer:
        """Create a post"""
        try:
            category = await Category.objects.aget(pk=data.category_id)
            post = await Post.objects.acreate(**data.dump(), category=category)
            return PostDetailSerializer.from_model(post)
        except Category.DoesNotExist as e:
            raise NotFound(detail="Category not found")
        except IntegrityError as e:
            raise BadRequest(detail="Bad request")

    async def update(self, request, pk: int, data: PostCreateSerializer):
        """Update a post"""
        try:
            category = await Category.objects.aget(pk=data.category_id)
            post = await Post.objects.aget(pk=pk)

            for key, value in data.dump().items():
                if hasattr(post, key):
                    setattr(post, key, value)
            post.category = category
            await post.asave()

            return PostDetailSerializer.from_model(post)
        except Category.DoesNotExist as e:
            raise NotFound(detail="Category not found")
        except IntegrityError as e:
            raise BadRequest(detail="Bad request")


@category_api.viewset("", tags=["Category"])
class CategoryViewSet(ViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer

    @paginate(CustomPagination)
    async def list(self, request: Request) -> PaginatedResponse:
        qs = Category.objects.all()

        return [CategoryListSerializer.from_model(category) async for category in qs]

    async def destroy(self, request: Request, pk: int) -> DeleteResponse:
        try:
            category = await Category.objects.aget(pk=pk)
            await category.adelete()
            return JSON({"data": {"id": pk, "message": "Category deleted."}})
        except Category.DoesNotExist as e:
            raise NotFound(detail="Category object does not found")

    async def create(self, request: Request, data: CategoryCreateSerializer):
        category = await Category.objects.acreate(**data.dump())

        return CategoryDetailSerializer.from_model(category)

    async def update(
        self, request: Request, data: CategoryCreateSerializer, pk: int
    ) -> CategoryDetailSerializer:
        try:
            category = await Category.objects.aget(pk=pk)
            for key, value in data.dump().items():
                if hasattr(category, key):
                    setattr(category, key, value)
            await category.asave()
            return CategoryDetailSerializer.from_model(category)
        except Category.DoesNotExist:
            raise NotFound(detail="Category not found")
