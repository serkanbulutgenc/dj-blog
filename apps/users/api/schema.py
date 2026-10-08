from __future__ import annotations

from datetime import date  # noqa:TC003
from typing import Annotated

from django.urls import reverse
from ninja import ModelSchema
from ninja import Schema
from pydantic import Field
from pydantic import HttpUrl

from apps.users.models import Profile
from apps.users.models import User


class AddressInfoSchema(Schema):
    address: Annotated[str | None, Field(max_length=255)] = None
    city: Annotated[str | None, Field(max_length=100)] = None
    state: Annotated[str | None, Field(max_length=100)] = None
    zip_code: Annotated[str | None, Field(max_length=20)] = None


class ProfileInfoSchema(Schema):
    bio: Annotated[str | None, Field(max_length=500)] = None
    dob: Annotated[date | None, Field(description="Date of birth")] = None
    phone: Annotated[str | None, Field(pattern=r"^\+?1?\d{9,15}$")] = None
    social_media_links: Annotated[list[HttpUrl] | None, Field(max_length=5)] = None
    address: AddressInfoSchema | None = None


class ProfileSchema(ModelSchema):
    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "info"]


class UpdateUserSchema(ModelSchema):
    username: str
    profile: ProfileInfoSchema | None = None

    class Meta:
        model = User
        fields = ["username"]
        fields_optional = ["profile"]


class UserSchema(ModelSchema):
    url: str
    profile: ProfileSchema | None = None

    class Meta:
        model = User
        fields = ["username", "email"]

    @staticmethod
    def resolve_url(obj: User):
        return reverse("api-v1:retrieve_user", kwargs={"username": obj.username})
