from apps.blog.api.routers.categories import router as category_router
from apps.blog.api.routers.posts import router as post_router
from apps.blog.api.routers.tags import router as tag_router

__all__ = ["category_router", "post_router", "tag_router"]
