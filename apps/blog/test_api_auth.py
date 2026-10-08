from http import HTTPStatus

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from ninja.testing import TestClient

from apps.blog.api.routers.posts import router
from apps.blog.api.security import jwt_bearer_auth
from apps.blog.models import Post
from apps.users.models import User
from config.api import api_v1


def test_openapi_declares_jwt_bearer_auth():
    schema = api_v1.get_openapi_schema()
    assert schema["components"]["securitySchemes"]["JWTBearerAuth"] == {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    for operation in schema["paths"]["/api/v1/posts/"].values():
        assert operation["security"] == [{"JWTBearerAuth": []}]


def test_jwt_bearer_auth_preserves_allauth_validation(monkeypatch):
    user = User()
    payload = {"sub": "1"}
    validated_tokens = []

    def validate_token(token):
        validated_tokens.append(token)
        return user, payload

    monkeypatch.setattr(
        "allauth.headless.contrib.ninja.security.validate_access_token",
        validate_token,
    )
    request = RequestFactory().get(
        "/api/v1/posts/",
        headers={"Authorization": "Bearer test-access-token"},
    )
    request.user = AnonymousUser()

    assert jwt_bearer_auth(request) == payload
    assert request.user is user
    assert validated_tokens == ["test-access-token"]


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"AUTHORIZATION": "test-access-token"},
        {"AUTHORIZATION": "Bearer invalid-token"},
    ],
)
def test_posts_reject_unauthenticated_requests(monkeypatch, headers):
    monkeypatch.setattr(
        "allauth.headless.contrib.ninja.security.validate_access_token",
        lambda token: None,
    )
    response = TestClient(router).get("/", headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_posts_preserve_permission_checks(monkeypatch):
    monkeypatch.setattr(
        "allauth.headless.contrib.ninja.security.validate_access_token",
        lambda token: (AnonymousUser(), {"sub": "1"}),
    )
    response = TestClient(router).get(
        "/",
        headers={"AUTHORIZATION": "Bearer test-access-token"},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_posts_accept_bearer_token(monkeypatch):
    user = User(is_superuser=True, is_active=True)
    monkeypatch.setattr(
        "allauth.headless.contrib.ninja.security.validate_access_token",
        lambda token: (user, {"sub": "1"}),
    )
    monkeypatch.setattr(Post.objects, "all", Post.objects.none)
    response = TestClient(router).get(
        "/",
        headers={"AUTHORIZATION": "Bearer test-access-token"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"items": [], "count": 0}
