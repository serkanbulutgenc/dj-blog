from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Profile
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

# Register your models here.

@admin.register(get_user_model())
class UserModelAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        BaseUserAdmin.fieldsets[0],
        *BaseUserAdmin.fieldsets[2:],
    )
    list_display=["username", "email"]

@admin.register(Profile)
class ProfileModelAdmin(admin.ModelAdmin):
    list_display=["first_name", "last_name"]
