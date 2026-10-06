from __future__ import annotations

import pytest

from apps.users.tests.factories import UserFactory


@pytest.fixture
def user(db):
    return UserFactory.create()
