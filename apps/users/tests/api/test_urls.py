from __future__ import annotations

from typing import TYPE_CHECKING

from django.urls import resolve
from django.urls import reverse

if TYPE_CHECKING:
    from apps.users.models import User


def test_user_detail(user: User):
    assert (
        reverse("api-v1:retrieve_user", kwargs={"username": user.username})
        == f"/api/v1/users/{user.username}/"
    )
    assert (
        resolve(f"/api/v1/users/{user.username}/").view_name == "api-v1:retrieve_user"
    )


def test_user_list():
    assert reverse("api-v1:list_users") == "/api/v1/users/"
    assert resolve("/api/v1/users/").view_name == "api-v1:list_users"


def test_current_user():
    assert reverse("api-v1:retrieve_current_user") == "/api/v1/users/me/"
    assert resolve("/api/v1/users/me/").view_name == "api-v1:retrieve_current_user"


def test_update_user():
    assert (
        reverse("api-v1:update_user", kwargs={"username": "john"})
        == "/api/v1/users/john/"
    )
    assert resolve("/api/v1/users/john/").view_name == "api-v1:retrieve_user"
