from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
# Create your models here.

class AppUser(AbstractUser):
    first_name = None
    last_name = None

class Profile(models.Model):
    first_name = models.CharField('First Name', max_length=30, null=True, blank=True, help_text=_("First Name"))
    last_name = models.CharField('Last Name', max_length=50, null=True, blank=True, help_text=_("First Name"))
    dob=models.DateField('Dob', null=True, blank=True, help_text=_("Date of birth"))
    info=models.JSONField('Info',null=True, blank=True, help_text=_("Profile Information"))
    user=models.OneToOneField(AppUser, on_delete=models.CASCADE, related_name='profile', help_text=_('Profile User'))

    class Meta:
        verbose_name_plural=_('Profiles')
        verbose_name=_('Profile')

    def __str__(self) -> str:
        return self.first_name or 'Noname'

