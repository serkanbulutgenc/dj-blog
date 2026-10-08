import logging

from allauth.account.signals import user_signed_up
from django.dispatch import receiver

from .models import Profile
from .models import User

logger = logging.getLogger(__name__)


@receiver(user_signed_up, sender=User)
def create_profile_on_signup(request, user, **kwargs):
    _, profile_created = Profile.objects.get_or_create(user=user)
    if profile_created:
        logger.info("Profile created for user: %s", user.username)
