from django.contrib.admin.views.decorators import staff_member_required
from ninja import NinjaAPI

from apps.blog.api import category_router
from apps.blog.api import post_router
from apps.blog.api import tag_router
from apps.users.api.views import router as user_router

api_v1 = NinjaAPI(
    title="DjBlog API",
    docs_decorator=staff_member_required,
    version="1.0.0",
    urls_namespace="api-v1",
)

api_v1.add_router(prefix="/posts", router=post_router)
api_v1.add_router(prefix="/categories", router=category_router)
api_v1.add_router(prefix="/tags", router=tag_router)
api_v1.add_router(prefix="/users", router=user_router)
