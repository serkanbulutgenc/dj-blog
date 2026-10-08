from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from threading import Barrier

import pytest
from django.contrib.auth.models import Permission
from django.db import IntegrityError
from django.db import connection
from django.db import connections
from django.db import transaction
from django.db.models import QuerySet
from django.test import Client
from django.test.utils import CaptureQueriesContext

from apps.blog.factories import PostFactory
from apps.blog.models import Post
from apps.blog.models import PostLike
from apps.users.tests.factories import UserFactory
from config.api import api_v1

AUTH_HEADERS = {"Authorization": "Bearer likes-test-token"}


@pytest.fixture
def api_client(monkeypatch, client):
    user = UserFactory.create()
    monkeypatch.setattr(
        "allauth.headless.contrib.ninja.security.validate_access_token",
        lambda token: (user, {"sub": str(user.pk)}),
    )
    return client, user


def grant_permissions(user, *codenames):
    user.user_permissions.add(
        *Permission.objects.filter(
            content_type__app_label="blog",
            codename__in=codenames,
        ),
    )


@pytest.mark.django_db
def test_like_model_unique_users_and_posts():
    user, other_user = UserFactory.create_batch(2)
    post, other_post = PostFactory.create_batch(2)
    like = PostLike.objects.create(post=post, user=user)

    with pytest.raises(IntegrityError), transaction.atomic():
        PostLike.objects.create(post=post, user=user)

    PostLike.objects.create(post=post, user=other_user)
    PostLike.objects.create(post=other_post, user=user)
    assert post.likes.count() == 2  # noqa: PLR2004
    assert user.post_likes.count() == 2  # noqa: PLR2004
    assert other_post.likes.count() == 1
    assert like.created is not None


@pytest.mark.django_db
def test_like_cascades_without_deleting_unrelated_likes():
    user, other_user = UserFactory.create_batch(2)
    post, other_post = PostFactory.create_batch(2)
    PostLike.objects.create(post=post, user=user)
    PostLike.objects.create(post=post, user=other_user)
    surviving_like = PostLike.objects.create(post=other_post, user=other_user)

    user.delete()
    assert post.likes.count() == 1
    assert Post.objects.filter(pk=post.pk).exists()

    post.delete()
    assert list(PostLike.objects.values_list("pk", flat=True)) == [surviving_like.pk]
    assert type(other_user).objects.filter(pk=other_user.pk).exists()


@pytest.mark.django_db
def test_like_unlike_and_relike_are_idempotent(api_client):
    client, user = api_client
    post = PostFactory.create(owner=UserFactory.create())
    path = f"/api/v1/posts/{post.pk}/like"
    liked = {"post_id": post.pk, "likes_count": 1, "is_liked": True}
    unliked = {"post_id": post.pk, "likes_count": 0, "is_liked": False}
    assert not user.has_perm("blog.view_post")

    for _ in range(2):
        response = client.delete(path, headers=AUTH_HEADERS)
        assert response.status_code == HTTPStatus.OK
        assert response.json() == unliked
    for _ in range(2):
        response = client.put(path, headers=AUTH_HEADERS)
        assert response.status_code == HTTPStatus.OK
        assert response.json() == liked
    assert PostLike.objects.filter(post=post, user=user).count() == 1
    for _ in range(2):
        response = client.delete(path, headers=AUTH_HEADERS)
        assert response.status_code == HTTPStatus.OK
        assert response.json() == unliked
    response = client.put(path, headers=AUTH_HEADERS)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == liked


@pytest.mark.django_db
def test_like_own_post_ignores_client_supplied_user(api_client):
    client, user = api_client
    other_user = UserFactory.create()
    post = PostFactory.create(owner=user)
    response = client.put(
        f"/api/v1/posts/{post.pk}/like",
        data={"user_id": other_user.pk},
        content_type="application/json",
        headers=AUTH_HEADERS,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "post_id": post.pk,
        "likes_count": 1,
        "is_liked": True,
    }
    assert PostLike.objects.get(post=post).user == user


@pytest.mark.django_db
def test_unlike_only_removes_current_users_like(api_client):
    client, user = api_client
    post = PostFactory.create()
    other_users = UserFactory.create_batch(3)
    for other_user in other_users:
        PostLike.objects.create(post=post, user=other_user)
    path = f"/api/v1/posts/{post.pk}/like"
    response = client.put(path, headers=AUTH_HEADERS)
    assert response.json() == {
        "post_id": post.pk,
        "likes_count": 4,
        "is_liked": True,
    }
    for _ in range(2):
        response = client.delete(
            path,
            data={"user_id": other_users[0].pk},
            content_type="application/json",
            headers=AUTH_HEADERS,
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "post_id": post.pk,
            "likes_count": 3,
            "is_liked": False,
        }
    assert not PostLike.objects.filter(post=post, user=user).exists()
    assert set(post.likes.values_list("user_id", flat=True)) == {
        other_user.pk for other_user in other_users
    }


@pytest.mark.django_db
def test_distinct_authenticated_users_share_post_likes(client, monkeypatch):
    first_user, second_user = UserFactory.create_batch(2)
    post = PostFactory.create()
    users_by_token = {"first-user": first_user, "second-user": second_user}
    monkeypatch.setattr(
        "allauth.headless.contrib.ninja.security.validate_access_token",
        lambda token: (users_by_token[token], {"sub": str(users_by_token[token].pk)}),
    )
    first_headers = {"Authorization": "Bearer first-user"}
    second_headers = {"Authorization": "Bearer second-user"}
    path = f"/api/v1/posts/{post.pk}/like"

    response = client.put(path, headers=first_headers)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "post_id": post.pk,
        "likes_count": 1,
        "is_liked": True,
    }
    response = client.put(path, headers=second_headers)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "post_id": post.pk,
        "likes_count": 2,
        "is_liked": True,
    }
    response = client.delete(path, headers=second_headers)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "post_id": post.pk,
        "likes_count": 1,
        "is_liked": False,
    }
    response = client.put(path, headers=first_headers)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "post_id": post.pk,
        "likes_count": 1,
        "is_liked": True,
    }
    assert PostLike.objects.get(post=post).user == first_user


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["put", "delete"])
@pytest.mark.parametrize(
    "headers",
    [{}, {"Authorization": "Bearer invalid-token"}],
)
def test_like_endpoints_require_authentication(client, monkeypatch, method, headers):
    post = PostFactory.create()
    monkeypatch.setattr(
        "allauth.headless.contrib.ninja.security.validate_access_token",
        lambda token: None,
    )
    response = getattr(client, method)(
        f"/api/v1/posts/{post.pk}/like",
        headers=headers,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert not PostLike.objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["put", "delete"])
def test_like_unknown_post_returns_404(api_client, method):
    client, _ = api_client
    post = PostFactory.create()
    post_id = post.pk
    post.delete()
    response = getattr(client, method)(
        f"/api/v1/posts/{post_id}/like",
        headers=AUTH_HEADERS,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert not PostLike.objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["get", "post", "patch"])
def test_unsupported_methods_cannot_mutate_likes(api_client, method):
    client, _ = api_client
    post = PostFactory.create()
    response = getattr(client, method)(
        f"/api/v1/posts/{post.pk}/like",
        headers=AUTH_HEADERS,
    )
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    assert not PostLike.objects.exists()


@pytest.mark.django_db
def test_post_responses_report_state_and_preserve_visibility(api_client):
    client, user = api_client
    grant_permissions(user, "view_post", "change_post", "delete_post")
    own_post = PostFactory.create(owner=user)
    other_user = UserFactory.create()
    other_post = PostFactory.create(owner=other_user)
    empty_post = PostFactory.create(owner=user)
    PostLike.objects.create(post=own_post, user=user)
    PostLike.objects.create(post=own_post, user=other_user)
    PostLike.objects.create(post=other_post, user=user)

    response = client.get("/api/v1/posts/", headers=AUTH_HEADERS)
    assert response.status_code == HTTPStatus.OK
    items = {item["id"]: item for item in response.json()["items"]}
    assert set(items) == {own_post.pk, empty_post.pk}
    assert response.json()["count"] == 2  # noqa: PLR2004
    assert items[own_post.pk]["likes_count"] == 2  # noqa: PLR2004
    assert items[own_post.pk]["is_liked"] is True
    assert items[empty_post.pk]["likes_count"] == 0
    assert items[empty_post.pk]["is_liked"] is False

    response = client.get(f"/api/v1/posts/{other_post.pk}", headers=AUTH_HEADERS)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["likes_count"] == 1
    assert response.json()["is_liked"] is True
    assert "likes" not in response.json()

    response = client.delete(
        f"/api/v1/posts/{own_post.pk}/like",
        headers=AUTH_HEADERS,
    )
    assert response.json() == {
        "post_id": own_post.pk,
        "likes_count": 1,
        "is_liked": False,
    }
    response = client.get(f"/api/v1/posts/{own_post.pk}", headers=AUTH_HEADERS)
    assert response.status_code == HTTPStatus.OK
    assert response.json()["likes_count"] == 1
    assert response.json()["is_liked"] is False
    client.put(f"/api/v1/posts/{own_post.pk}/like", headers=AUTH_HEADERS)

    response = client.put(
        f"/api/v1/posts/{own_post.pk}",
        data={"title": "Updated own post", "likes_count": 100, "is_liked": False},
        content_type="application/json",
        headers=AUTH_HEADERS,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["likes_count"] == 2  # noqa: PLR2004
    assert response.json()["is_liked"] is True

    for method in ("put", "delete"):
        response = getattr(client, method)(
            f"/api/v1/posts/{other_post.pk}",
            data={"title": "Forbidden change"},
            content_type="application/json",
            headers=AUTH_HEADERS,
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
    other_post.refresh_from_db()
    assert other_post.owner == other_user
    assert own_post.likes.count() == 2  # noqa: PLR2004


@pytest.mark.django_db
def test_list_likes_preserve_filters_pagination_and_superuser_visibility(api_client):
    client, user = api_client
    user.is_superuser = True
    user.save()
    first = PostFactory.create(
        title="Matching post",
        slug="matching-first-post",
        owner=UserFactory.create(),
    )
    second = PostFactory.create(
        title="Matching post",
        slug="matching-second-post",
        owner=user,
    )
    PostFactory.create(title="Different post", owner=user)
    PostLike.objects.create(post=first, user=user)
    PostLike.objects.create(post=second, user=UserFactory.create())

    response = client.get(
        "/api/v1/posts/",
        {"title": "Matching post", "page_size": 1, "page": 1},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["count"] == 2  # noqa: PLR2004
    assert len(response.json()["items"]) == 1
    item = response.json()["items"][0]
    assert item["id"] == second.pk
    assert item["likes_count"] == 1
    assert item["is_liked"] is False

    response = client.get(
        "/api/v1/posts/",
        {"title": "Matching post", "page_size": 1, "page": 2},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["count"] == 2  # noqa: PLR2004
    assert len(response.json()["items"]) == 1
    item = response.json()["items"][0]
    assert item["id"] == first.pk
    assert item["likes_count"] == 1
    assert item["is_liked"] is True


@pytest.mark.django_db
def test_like_does_not_grant_read_permission(api_client):
    client, _ = api_client
    post = PostFactory.create()
    response = client.put(f"/api/v1/posts/{post.pk}/like", headers=AUTH_HEADERS)
    assert response.status_code == HTTPStatus.OK
    for path in ("/api/v1/posts/", f"/api/v1/posts/{post.pk}"):
        response = client.get(path, headers=AUTH_HEADERS)
        assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_list_like_queries_do_not_grow_with_post_count(api_client):
    client, user = api_client
    grant_permissions(user, "view_post")
    post = PostFactory.create(owner=user)
    PostLike.objects.create(post=post, user=user)

    def list_like_queries():
        with CaptureQueriesContext(connection) as queries:
            response = client.get("/api/v1/posts/", headers=AUTH_HEADERS)
        assert response.status_code == HTTPStatus.OK
        return response.json(), [
            query["sql"] for query in queries if "blog_postlike" in query["sql"]
        ]

    single, single_queries = list_like_queries()
    PostFactory.create_batch(4, owner=user)
    multiple, multiple_queries = list_like_queries()
    assert len(single["items"]) == 1
    assert len(multiple["items"]) == 5  # noqa: PLR2004
    assert len(single_queries) == len(multiple_queries)
    assert len(multiple_queries) <= 2  # noqa: PLR2004


def test_like_openapi_declares_auth_and_response_shape():
    schema = api_v1.get_openapi_schema()
    operations = schema["paths"]["/api/v1/posts/{post_id}/like"]
    assert set(operations) == {"put", "delete"}
    for operation in operations.values():
        assert operation["security"] == [{"JWTBearerAuth": []}]
    response_schema = schema["components"]["schemas"]["PostLikeStateSchema"]
    assert set(response_schema["properties"]) == {
        "post_id",
        "likes_count",
        "is_liked",
    }
    assert set(response_schema["required"]) == {
        "post_id",
        "likes_count",
        "is_liked",
    }


@pytest.mark.django_db(transaction=True)
def test_concurrent_likes_create_one_row(monkeypatch):
    if connection.vendor != "postgresql":
        pytest.skip("Concurrent like test requires PostgreSQL")
    user = UserFactory.create()
    post = PostFactory.create()
    monkeypatch.setattr(
        "allauth.headless.contrib.ninja.security.validate_access_token",
        lambda token: (user, {"sub": str(user.pk)}),
    )
    barrier = Barrier(2)
    original_create = QuerySet.create

    def synchronized_create(queryset, **kwargs):
        if queryset.model is PostLike:
            barrier.wait(timeout=10)
        return original_create(queryset, **kwargs)

    monkeypatch.setattr(QuerySet, "create", synchronized_create)

    def like_in_separate_connection():
        try:
            return Client().put(
                f"/api/v1/posts/{post.pk}/like",
                headers=AUTH_HEADERS,
            )
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(lambda _: like_in_separate_connection(), range(2)),
        )
    for response in responses:
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "post_id": post.pk,
            "likes_count": 1,
            "is_liked": True,
        }
    assert PostLike.objects.filter(post=post, user=user).count() == 1
