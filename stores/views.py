from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Inventory
from .serializers import InventoryListSerializer


class StoreInventoryListView(APIView):

    def get(self, request, store_id):

        cache_key = f"inventory:store:{store_id}"

        # -------------------------
        # Redis cache lookup
        # -------------------------

        cached_inventory = cache.get(cache_key)

        if cached_inventory is not None:
            return Response(cached_inventory)

        # -------------------------
        # PostgreSQL query
        # -------------------------

        inventory = (
            Inventory.objects
            .filter(store_id=store_id)
            .select_related(
                "product",
                "product__category",
            )
            .order_by("product__title")
        )

        # -------------------------
        # Serialize
        # -------------------------

        serializer = InventoryListSerializer(
            inventory,
            many=True,
        )

        data = serializer.data

        # -------------------------
        # Cache for 5 minutes
        # -------------------------

        cache.set(
            cache_key,
            data,
            timeout=300,
        )

        return Response(data)