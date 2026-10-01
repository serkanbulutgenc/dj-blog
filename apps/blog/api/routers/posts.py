import logging

from django.shortcuts import get_object_or_404
from ninja import Query
from ninja import Router
from ninja.pagination import PageNumberPagination
from ninja.pagination import paginate

from apps.blog.api.schemas import PostDetailSchema
from apps.blog.api.schemas import PostFilterSchema
from apps.blog.api.schemas import PostInSchema
from apps.blog.api.schemas import PostListSchema
from apps.blog.api.schemas import PostOutSchema
from apps.blog.models import Category
from apps.blog.models import Post
from apps.blog.models import Tag

logger = logging.getLogger(__name__)

router = Router(tags=["posts"])


@router.get("/", response={200: list[PostListSchema]})
@paginate(PageNumberPagination)
def list_post(request, filters: Query[PostFilterSchema]):
    posts = Post.objects.all()
    return filters.filter(posts)


@router.get("/{post_id}", response={200: PostDetailSchema})
def get_post(request, post_id: int):
    return get_object_or_404(Post, id=post_id)


@router.post("/", response={201: PostOutSchema})
def create_post(request, payload: PostInSchema):
    created_fields = payload.dict(exclude_unset=True)
    category_id = created_fields.pop("category", None)
    post_category = get_object_or_404(Category, id=category_id) if category_id else None

    post_tag_ids = created_fields.pop("tags", None)
    post_tags = Tag.objects.filter(id__in=post_tag_ids) if post_tag_ids else None

    logger.debug(
        "Creating post with fields: %s, category: %s, tags: %s",
        created_fields,
        post_category,
        post_tags,
    )

    post = Post.objects.create(**created_fields, category=post_category)

    if post_tags:
        post.tags.set(post_tags)
    return post


@router.put("/{post_id}", response={200: PostDetailSchema})
def update_post(request, post_id: int, payload: PostInSchema):
    post = get_object_or_404(Post, id=post_id)
    updated_fields = payload.dict(exclude_unset=True)

    if updated_fields:
        category_id = updated_fields.pop("category", None)
        post_tag_ids = updated_fields.pop("tags", None)
        post_tags = Tag.objects.filter(id__in=post_tag_ids) if post_tag_ids else None

        if category_id:
            post_category = get_object_or_404(Category, id=category_id)
            post.category = post_category
        for attr, value in updated_fields.items():
            setattr(post, attr, value)
        if post_tags:
            post.tags.set([2, 3])
        else:
            post.tags.clear()
        post.save()
    return post


@router.delete("/{post_id}", response={204: None})
def delete_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
