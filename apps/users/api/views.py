from __future__ import annotations

import logging as logger
from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from ninja import Router

from apps.users.api.schema import UpdateUserSchema
from apps.users.api.schema import UserSchema
from apps.users.models import User

logger = logger.getLogger(__name__)

if TYPE_CHECKING:
    from django.db.models import QuerySet

router = Router(tags=["users"])


def _get_users_queryset(request) -> QuerySet[User]:
    return User.objects.filter(pk=request.user.pk).select_related("profile")


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
    return user


@router.patch("/{username}/", response=UserSchema)
def update_user(request, username: str, data: UpdateUserSchema):
    logger.info("Updating user with data: %s", data)
    users_qs = _get_users_queryset(request)
    user = get_object_or_404(users_qs, username=username)
    user.username = data.username
    if data.profile is not None:
        user.profile.info = data.profile.model_dump(mode="json", exclude_unset=True)
        user.profile.save()
    user.save()
    return user
