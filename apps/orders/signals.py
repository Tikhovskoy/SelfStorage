from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.orders.services import ensure_client


@receiver(post_save, sender=User)
def create_client_profile(sender, instance, created, raw=False, **kwargs):
    """Каждому новому пользователю создаёт профиль клиента."""
    if created and not raw:
        ensure_client(instance)
