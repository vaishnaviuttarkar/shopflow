from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Inventory


@receiver(post_save, sender=Inventory)
def invalidate_inventory_cache(
    sender,
    instance,
    **kwargs,
):
    cache_key = f"inventory:store:{instance.store_id}"

    cache.delete(cache_key)


@receiver(post_delete, sender=Inventory)
def invalidate_inventory_cache_on_delete(
    sender,
    instance,
    **kwargs,
):
    cache_key = f"inventory:store:{instance.store_id}"

    cache.delete(cache_key)