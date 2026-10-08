from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

from apps.users.models import Profile

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest

    from apps.users.models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def save_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        form=None,
    ) -> User:
        user = super().save_user(request, sociallogin, form)
        data = sociallogin.account.extra_data
        profile, _ = Profile.objects.get_or_create(user=user)
        if first_name := data.get("first_name"):
            profile.first_name = first_name
        if last_name := data.get("last_name"):
            profile.last_name = last_name
        if name := data.get("name"):
            info = profile.info.copy() if isinstance(profile.info, dict) else {}
            info.setdefault("name", name)
            profile.info = info
        profile.save(update_fields=["first_name", "last_name", "info"])
        return user
