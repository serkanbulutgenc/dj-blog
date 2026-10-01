from django.shortcuts import get_object_or_404
from ninja import Query
from ninja import Router
from ninja.pagination import PageNumberPagination
from ninja.pagination import paginate

from apps.blog.models import Post

from .schemas import PostDetailSchema
from .schemas import PostFilterSchema
from .schemas import PostInSchema
from .schemas import PostListSchema

router = Router(tags=["blog"])


@router.get("/posts", response={200: list[PostListSchema]})
@paginate(PageNumberPagination)
def list_post(request, filters: Query[PostFilterSchema]):
    posts = Post.objects.all()
    return filters.filter(posts)


@router.get("/posts/{post_id}", response={200: PostDetailSchema})
def get_post(request, post_id: int):
    return get_object_or_404(Post, id=post_id)


@router.post("/posts", response={201: PostDetailSchema})
def create_post(request, payload: PostInSchema):
    return Post.objects.create(**payload.dict(exclude_unset=True))


@router.put("/posts/{post_id}", response={200: PostDetailSchema})
def update_post(request, post_id: int, payload: PostInSchema):
    post = get_object_or_404(Post, id=post_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(post, attr, value)
    post.save()
    return post


@router.delete("/posts/{post_id}", response={204: None})
def delete_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
