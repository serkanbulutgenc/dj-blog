from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import django_auth

from apps.users.api.schema import ProfileInfoSchema
from apps.users.api.schema import UpdateUserSchema
from apps.users.api.schema import UserSchema
from apps.users.models import Profile
from apps.users.models import User

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django.db.models import QuerySet

router = Router(tags=["users"], auth=django_auth)


def _get_users_queryset(request) -> QuerySet[User]:
    return User.objects.filter(pk=request.user.pk).select_related("profile")


def _merge_profile_info(
    existing: dict[str, object],
    updates: dict[str, object],
) -> dict[str, object]:
    merged = existing.copy()
    for key, value in updates.items():
        current_value = merged.get(key)
        if isinstance(current_value, dict) and isinstance(value, dict):
            merged[key] = _merge_profile_info(current_value, value)
        else:
            merged[key] = value
    return merged


def _update_profile(user: User, data: ProfileInfoSchema) -> None:
    profile, _ = Profile.objects.get_or_create(user=user)
    user.profile = profile
    existing_info = profile.info
    if existing_info is None:
        existing_info = {}
    elif not isinstance(existing_info, dict):
        error_message = "Profile info must be a JSON object to apply a partial update."
        raise TypeError(error_message)
    profile.info = _merge_profile_info(
        existing_info,
        data.model_dump(mode="json", exclude_unset=True),
    )
    profile.save(update_fields=["info"])


@router.get("/", response=list[UserSchema])
def list_users(request):
    return _get_users_queryset(request)


@router.get("/me/", response=UserSchema)
def retrieve_current_user(request):
    return request.user


@router.get("/{username}/", response=UserSchema)
def retrieve_user(request, username: str):
    users_qs = _get_users_queryset(request)
    return get_object_or_404(users_qs, username=username)


@router.patch("/me/", response=UserSchema)
def update_current_user(request, data: UpdateUserSchema):
    user = request.user
    user.username = data.username
    user.save()
    if data.profile is not None:
        _update_profile(user, data.profile)
    return user


@router.patch("/{username}/", response=UserSchema)
def update_user(request, username: str, data: UpdateUserSchema):
    logger.info("Updating user with data: %s", data)
    users_qs = _get_users_queryset(request)
    user = get_object_or_404(users_qs, username=username)
    user.username = data.username
    if data.profile is not None:
        _update_profile(user, data.profile)
    user.save()
    return user
