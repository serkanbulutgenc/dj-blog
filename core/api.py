from ninja_extra import NinjaExtraAPI
from apps.blog.api import PostModelController

app = NinjaExtraAPI(
    title="DjBlog Api", version="0.0.1", description="A blog API with django"
)

app.register_controllers(PostModelController)
