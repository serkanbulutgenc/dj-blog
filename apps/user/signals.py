from django.dispatch import receiver 
from django.db.models.signals import post_save 
from .models import Profile
from django.contrib.auth import get_user_model
#allauth.account.signals.user_signed_up(request, user)
from allauth.account.signals import user_signed_up

@receiver(user_signed_up)
def create_user_profile(request, user, **kwargs):
    print( request, user, kwargs)
    if user:
        Profile.objects.create(user=user)