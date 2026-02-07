from django.shortcuts import get_object_or_404
#from allauth.headless.contrib.ninja.security import jwt_token_auth, x_session_token_auth
from .models import Post, Category
from django_bolt import BoltAPI
from django_bolt.exceptions import NotFound
from django_bolt.responses import JSON
from .schemas import PostListSerializer,PostCreateSerializer, PostDetailSerializer, CategoryListSerializer


# Define a FilterSchema for your model
api = BoltAPI(prefix="/posts",openapi_config={"summary":"Post endpoint"})

@api.get('/', response_model=list[PostListSerializer])
async def list_posts(request)->list[PostListSerializer]:
    return [PostListSerializer.from_model(post) async for post in Post.objects.select_related('category')[:20]]

@api.get('/{post_id}', response_model=PostDetailSerializer)
async def get_post(request, post_id:int)->PostDetailSerializer:
    try:
        post = await Post.objects.select_related('category').aget(id=post_id)
        return PostDetailSerializer.from_model(post)
    except Post.DoesNotExist as e:
        return NotFound(detail='The post not found.')

@api.delete('/{post_id}', status_code=200)
async def delete_post(request, post_id:int):
    try:
        post = await Post.objects.aget(id=post_id)
        await post.adelete()
        return {"data":{"id":post_id, "message":"Post Deleted"}}
    except Post.DoesNotExist as e:
        NotFound(detail="Post not found")
