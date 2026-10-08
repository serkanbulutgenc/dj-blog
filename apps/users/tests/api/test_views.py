from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from apps.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from django.test import Client

    from apps.users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return UserFactory.create()


def test_list_users_as_anonymous_user(client: Client):
    response = client.get(reverse("api-v1:list_users"))

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_list_users_as_authenticated_user(client: Client, user: User):
    client.force_login(user)
    # Another user, excluded from the response
    UserFactory.create()

    response = client.get(reverse("api-v1:list_users"))

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            "email": user.email,
            "profile": {"first_name": "", "info": None, "last_name": ""},
            "url": f"/api/v1/users/{user.username}/",
            "username": user.username,
        },
    ]


def test_retrieve_current_user(client: Client, user: User):
    client.force_login(user)

    response = client.get(
        reverse("api-v1:retrieve_current_user"),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "email": user.email,
        "profile": {"first_name": "", "info": None, "last_name": ""},
        "url": f"/api/v1/users/{user.username}/",
        "username": user.username,
    }


def test_retrieve_user(client: Client, user: User):
    client.force_login(user)

    response = client.get(
        reverse("api-v1:retrieve_user", kwargs={"username": user.username}),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "email": user.email,
        "profile": {"first_name": "", "info": None, "last_name": ""},
        "url": f"/api/v1/users/{user.username}/",
        "username": user.username,
    }


def test_retrieve_another_user(client: Client, user: User):
    client.force_login(user)
    user_2 = UserFactory.create()

    response = client.get(
        reverse("api-v1:retrieve_user", kwargs={"username": user_2.username}),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Not Found"}


def test_update_current_user(client: Client):
    user = UserFactory.create(username="old")
    client.force_login(user)

    response = client.patch(
        reverse("api-v1:update_current_user"),
        data='{"username": "old"}',
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.OK, response.json()
    assert response.json() == {
        "email": user.email,
        "profile": {"first_name": "", "info": None, "last_name": ""},
        "username": "old",
        "url": "/api/v1/users/old/",
    }


def test_update_user(client: Client):
    user = UserFactory.create(username="old")
    client.force_login(user)

    response = client.patch(
        reverse("api-v1:update_user", kwargs={"username": "old"}),
        data='{"username": "old"}',
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.OK, response.json()
    assert response.json() == {
        "email": user.email,
        "profile": {"first_name": "", "info": None, "last_name": ""},
        "url": "/api/v1/users/old/",
        "username": "old",
    }


def test_update_current_user_profile_merges_partial_info(client: Client, user: User):
    user.profile.info = {
        "bio": "Existing bio",
        "phone": "+12025550123",
        "address": {"city": "Existing city", "state": "CA"},
    }
    user.profile.save(update_fields=["info"])
    client.force_login(user)

    response = client.patch(
        reverse("api-v1:update_current_user"),
        data='{"username": "updated", "profile": {"address": {"city": "New city"}}}',
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.OK, response.json()
    assert response.json()["profile"]["info"] == {
        "address": {"city": "New city", "state": "CA"},
        "bio": "Existing bio",
        "phone": "+12025550123",
    }
    user.refresh_from_db()
    assert user.profile.info == response.json()["profile"]["info"]


def test_update_user_profile_creates_missing_profile(client: Client, user: User):
    user.profile.delete()
    client.force_login(user)

    response = client.patch(
        reverse("api-v1:update_user", kwargs={"username": user.username}),
        data='{"username": "updated", "profile": {"bio": "Added profile"}}',
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.OK, response.json()
    assert response.json()["profile"]["info"] == {"bio": "Added profile"}
