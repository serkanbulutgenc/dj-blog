from django.db.models.signals import post_save 
from django.dispatch import receiver 
from apps.blog.models import Post, Category 

@receiver(post_save, sender=Category)
def signal_receiver(sender, **kwargs):
    print(sender, kwargs)