from __future__ import annotations

from factory import Faker
from factory import post_generation
from factory.django import DjangoModelFactory

from apps.users.models import Profile
from apps.users.models import User


class UserFactory(DjangoModelFactory[User]):
    username = Faker("user_name")
    email = Faker("email")

    @post_generation
    def password(self: User, create: bool, extracted: str | None, **kwargs):  # noqa: FBT001
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)
        if create:
            self.save()

    @post_generation
    def profile(self: User, create: bool, extracted, **kwargs):  # noqa: FBT001
        if create:
            Profile.objects.get_or_create(user=self)

    class Meta:
        model = User
        django_get_or_create = ["username"]
        skip_postgeneration_save = True
