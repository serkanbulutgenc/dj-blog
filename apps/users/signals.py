import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile
from .models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, first_name="change", last_name="me")
        logger.info("Profile created for user: %s", instance.username)
    else:
        logger.info("Profile not created for user: %s", instance.username)
