from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from stores.models import Store, Inventory
from products.models import Product

from .models import Order, OrderItem
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderItemSerializer
)

from django.db.models import Count
from rest_framework.generics import ListAPIView

from .tasks import send_order_confirmation

class OrderCreateView(APIView):

    def post(self, request):
        serializer = OrderCreateSerializer(
            data=request.data
        )

        # pserializer = OrderItemSerializer(
        #     pdata=request.data
        # )

        serializer.is_valid(raise_exception=True)
        # pserializer.is_valid(raise_exception=True)

        store_id = serializer.validated_data["store_id"]
        items = serializer.validated_data["items"]
        # product_title = pserializer.validated_data["product_title"]

        with transaction.atomic():

            store = Store.objects.get(id=store_id)

            product_ids = [
                item["product_id"]
                for item in items
            ]

            inventories = (
                Inventory.objects
                .select_for_update()
                .select_related("product")
                .filter(
                    store=store,
                    product_id__in=product_ids,
                )
            )

            inventory_map = {
                inventory.product_id: inventory
                for inventory in inventories
            }

            # products = Product.objects.filter(id__in=product_ids)

            # product_map = {
            #     product.id: product
            #     for product in products
            # }

            insufficient_stock = []

            for item in items:

                product_id = item["product_id"]
                requested = item["quantity_requested"]

                inventory = inventory_map.get(product_id)
                # product = product_map.get(product_id)

                if inventory is None:
                    insufficient_stock.append({
                        "product_id": product_id,
                        # "product_title": product.title if product else "Unknown product",
                        "reason": "Product not available at this store.",
                    })

                elif inventory.quantity < requested:
                    insufficient_stock.append({
                        "product_id": product_id,
                        # "product_title": product.title,
                        "reason": "Insufficient stock.",
                        "available": inventory.quantity,
                        "requested": requested,
                    })

            if insufficient_stock:

                order = Order.objects.create(
                    store=store,
                    status=Order.Status.REJECTED,
                )

                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product_id=item["product_id"],
                        quantity_requested=item["quantity_requested"],
                    )

                ptitle = inventory.product.title
                msg = f"{ptitle} is not available"

                return Response(
                    {
                        "order": OrderSerializer(order).data,
                        "errors": insufficient_stock,
                        "message": msg
                    },
                    status=status.HTTP_201_CREATED,
                )

            # All products have enough stock.
            order = Order.objects.create(
                store=store,
                status=Order.Status.CONFIRMED,
            )

            for item in items:

                product_id = item["product_id"]
                requested = item["quantity_requested"]

                inventory = inventory_map[product_id]

                inventory.quantity -= requested
                inventory.save(
                    update_fields=["quantity"]
                )

                OrderItem.objects.create(
                    order=order,
                    product_id=product_id,
                    quantity_requested=requested,
                )

            # Trigger Celery only after the transaction commits successfully
            transaction.on_commit(
                lambda: send_order_confirmation.delay(order.id)
            )
            
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )

class StoreOrderListView(ListAPIView):
    serializer_class = OrderListSerializer

    def get_queryset(self):
        store_id = self.kwargs["store_id"]

        return (
            Order.objects
            .filter(store_id=store_id)
            .annotate(
                total_items=Count("items")
            )
            .order_by("-created_at")
        )