from __future__ import annotations

import pytest
from allauth.account.signals import user_signed_up

from apps.users.models import Profile
from apps.users.models import User


def test_user_get_absolute_url(user: User):
    assert user.get_absolute_url() == f"/users/{user.username}/"


@pytest.mark.django_db
def test_signup_signal_creates_profile():
    user = User.objects.create_user(username="new-signup")

    user_signed_up.send(sender=User, request=None, user=user)

    assert Profile.objects.filter(user=user).exists()
