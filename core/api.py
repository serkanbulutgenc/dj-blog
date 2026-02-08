from django_bolt import BoltAPI
from django_bolt.health import register_health_checks
from apps.blog.api import post_api, category_api

api = BoltAPI(
    enable_logging=True,
    trailing_slash="append",
    prefix="/api",
)
api.mount("/api/posts", post_api)
api.mount("/api/categories", category_api)
register_health_checks(api=api)
