from django_bolt import BoltAPI
from apps.blog.api import api as post_api 

api = BoltAPI(
    enable_logging=True,
    trailing_slash='strip',
    prefix="/api",
)

api.mount('/api', post_api)

