from ninja_schema import Schema
from ninja_extra import api_controller, ControllerBase, http_get, route
from django.contrib.auth import get_user_model
from allauth.headless.contrib.ninja.security import x_session_token_auth
from ninja_extra.permissions import IsAuthenticated
from ninja.security import django_auth

@api_controller('/me')
class ProfileController(ControllerBase):
    @route.get('/', auth=[x_session_token_auth], description="Profile information", summary='Gets the authenticated user profile information', tags=['profile'])
    def get_profile(self):
        print("meeee")
        user_profile = self.context.request.user
        print("profile",user_profile)
        return {
            "first_name":user_profile.first_name,
            "last_name":user_profile.last_name
        }
