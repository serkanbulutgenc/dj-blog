from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for Django Blog.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(
        _("First Name"),
        blank=True,
        max_length=255,
        help_text=_("User's first name."),
    )
    last_name = models.CharField(
        _("Last Name"),
        blank=True,
        max_length=255,
        help_text=_("User's last name."),
    )
    info = models.JSONField(
        _("Info"),
        blank=True,
        null=True,
        help_text=_("User information in JSON format."),
    )

    def __str__(self) -> str:
        return self.user.username

    def get_absolute_url(self):
        return reverse("model_detail", kwargs={"pk": self.pk})
