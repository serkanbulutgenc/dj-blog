import logging
from functools import wraps

from django.db.models import Count
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination
from ninja.pagination import paginate

from apps.blog.api.schemas import PostDetailSchema
from apps.blog.api.schemas import PostFilterSchema
from apps.blog.api.schemas import PostInSchema
from apps.blog.api.schemas import PostLikeStateSchema
from apps.blog.api.schemas import PostListSchema
from apps.blog.api.schemas import PostOutSchema
from apps.blog.api.security import jwt_bearer_auth
from apps.blog.models import Category
from apps.blog.models import Post
from apps.blog.models import PostLike
from apps.blog.models import Tag

logger = logging.getLogger(__name__)

router = Router(tags=["Posts"], auth=[jwt_bearer_auth])


def require_perm(perm: str):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.has_perm(perm):
                raise HttpError(403, "Permission denied")
            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def _with_like_state(request, posts: QuerySet[Post]) -> QuerySet[Post]:
    return posts.annotate(
        likes_count=Count("likes", distinct=True),
        is_liked=Exists(
            PostLike.objects.filter(post_id=OuterRef("pk"), user_id=request.user.pk),
        ),
    )


def _get_post(request, post_id: int):
    return get_object_or_404(
        _with_like_state(request, Post.objects.all()),
        id=post_id,
    )


def _check_post_owner(request, post: Post) -> None:
    if post.owner != request.user and not request.user.is_superuser:
        raise HttpError(403, "Permission denied")


@router.get("/", response={200: list[PostListSchema]})
@paginate(PageNumberPagination)
@require_perm("blog.view_post")
def list_post(request, filters: Query[PostFilterSchema]):
    logger.info("Listing posts auth: %s", request.user)
    if request.user.is_superuser:
        posts = Post.objects.all()
    else:
        posts = Post.objects.filter(owner=request.user)
    # Aggregate annotations suppress implicit model ordering.
    posts = filters.filter(posts).order_by("-created")
    return _with_like_state(request, posts)


@router.get("/{post_id}", response={200: PostDetailSchema})
@require_perm("blog.view_post")
def get_post(request, post_id: int):
    return _get_post(request, post_id)


@router.post("/", response={201: PostOutSchema})
@require_perm("blog.add_post")
def create_post(request, payload: PostInSchema):
    created_fields = payload.dict(exclude_unset=True)

    category_id = created_fields.pop("category", None)
    post_category = get_object_or_404(Category, id=category_id) if category_id else None

    post_tag_ids = created_fields.pop("tags", None)
    post_tags = Tag.objects.filter(id__in=post_tag_ids) if post_tag_ids else None

    post = Post.objects.create(
        **created_fields,
        category=post_category,
        owner=request.user,
    )

    if post_tags:
        post.tags.set(post_tags)
    return post


@router.put("/{post_id}", response={200: PostDetailSchema})
@require_perm("blog.change_post")
def update_post(request, post_id: int, payload: PostInSchema):
    post = _get_post(request, post_id)

    _check_post_owner(request, post)

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
            post.tags.set(post_tags)
        else:
            post.tags.clear()
        post.save()
    return _get_post(request, post_id)


@router.delete("/{post_id}", response={204: None})
@require_perm("blog.delete_post")
def delete_post(request, post_id: int):

    post = _get_post(request, post_id)
    _check_post_owner(request, post)
    post.delete()


@router.put("/{post_id}/like", response={200: PostLikeStateSchema})
def like_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    PostLike.objects.get_or_create(post=post, user=request.user)
    return _get_post(request, post_id)


@router.delete("/{post_id}/like", response={200: PostLikeStateSchema})
def unlike_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    PostLike.objects.filter(post=post, user=request.user).delete()
    return _get_post(request, post_id)
