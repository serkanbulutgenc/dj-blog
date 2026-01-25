from ninja_extra import ModelControllerBase, ModelConfig, api_controller
from allauth.headless.contrib.ninja.security import jwt_token_auth, x_session_token_auth
from allauth.headless.adapter import DefaultHeadlessAdapter
from .models import Post, Category


@api_controller("/posts", tags=["blog"], auth=[jwt_token_auth])
class PostModelController(ModelControllerBase):
    model_config = ModelConfig(model=Post)
