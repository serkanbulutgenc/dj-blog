from django.contrib.admin.views.decorators import staff_member_required
from ninja import NinjaAPI
from ninja.security import SessionAuth

from apps.blog.api import category_router
from apps.blog.api import post_router
from apps.blog.api import tag_router

api_v1 = NinjaAPI(
    auth=SessionAuth(),
    docs_decorator=staff_member_required,
    version="1.0.0",
    urls_namespace="api-v1",
)

api_v1.add_router(prefix="/users/", router="apps.users.api.views.router")
api_v1.add_router(prefix="/posts", router=post_router)
api_v1.add_router(prefix="/categories", router=category_router)
api_v1.add_router(prefix="/tags", router=tag_router)
