from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Workspace


@receiver(post_save, sender=User)
def ensure_workspace(sender, instance: User, created: bool, **kwargs):
    # Create a workspace for new users and also backfill if missing
    Workspace.objects.get_or_create(
        owner=instance,
        defaults={"name": f"{instance.username}'s Workspace"}
    )