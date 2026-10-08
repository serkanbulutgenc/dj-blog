# Django Blog

This is a sample blog project with Django.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      uv run python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Authorizing requests in Swagger

1. Open `/api/v1/docs` and sign in with a staff account if redirected to the
   admin login page. This login controls access to the documentation; it does
   not authenticate requests to the posts API.
2. Obtain an **access token** from the allauth headless login flow, just as you
   do when calling the API from the terminal.
3. Click **Authorize**, paste only the access token (without the `Bearer `
   prefix), and confirm. Swagger adds `Authorization: Bearer <access-token>`
   to requests for protected endpoints.
4. Use **Try it out** on a posts endpoint. The token's user still needs the
   corresponding blog permissions. A `401` indicates missing or invalid
   authentication; a `403` indicates insufficient permissions.

Use an access token, not a refresh token or an `X-Session-Token`. When the
access token expires, obtain a new one and authorize again.

### Post likes

Any authenticated user can like any existing post, including their own, without
blog model permissions. Each user has at most one like per post, enforced by a
database constraint. Users can remove their own like and like the post again.

Send an allauth access token in the `Authorization: Bearer <access-token>`
header. No request body or user ID is needed:

```http
PUT /api/v1/posts/123/like
Authorization: Bearer <access-token>
```

```json
{"post_id": 123, "likes_count": 1, "is_liked": true}
```

```http
DELETE /api/v1/posts/123/like
Authorization: Bearer <access-token>
```

```json
{"post_id": 123, "likes_count": 0, "is_liked": false}
```

Both operations return `200`. Repeated PUTs do not add duplicate likes, and
repeated DELETEs do not remove other users' likes. Missing or invalid
authentication returns `401`; an unknown post returns `404`. GET does not
change likes. Totals reflect the database when read and can change as other
users like or unlike the post.

Post list, detail, and update responses also include read-only `likes_count`
and `is_liked` fields. Existing read and CRUD permissions are unchanged:
reading posts still requires `blog.view_post`, and non-superusers still list
only their own posts. Like endpoints intentionally allow authenticated users
without read permission to discover a post's existence and like count.

Apply the new migration before using this feature:

```sh
uv run python manage.py migrate
```

### Type checks

Running type checks with mypy:

    uv run mypy django_blog

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    uv run coverage run -m pytest
    uv run coverage html
    uv run open htmlcov/index.html

#### Running tests with pytest

    uv run pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally.html#using-webpack-or-gulp).

## Deployment

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/3-deployment/deployment-with-docker.html).
