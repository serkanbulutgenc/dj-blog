import logging

from allauth.account.signals import user_signed_up
from django.dispatch import receiver

from .models import Profile
from .models import User

logger = logging.getLogger(__name__)


@receiver(user_signed_up, sender=User)
def create_profile_on_signup(request, user, **kwargs):
    if user:
        Profile.objects.create(user=user, first_name="change", last_name="me")
        logger.info("Profile created for user: %s", user.username)
    else:
        logger.info("Profile not created for user: %s", user.username)
