from django.test import TestCase
from rest_framework.test import APIClient

from products.models import Category, Product
from stores.models import Store, Inventory
from orders.models import Order, OrderItem


class ShopFlowAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.category = Category.objects.create(
            name="Electronics"
        )

        self.product = Product.objects.create(
            title="Laptop",
            description="Test laptop",
            price=50000,
            category=self.category
        )

        self.product2 = Product.objects.create(
            title="Mouse",
            description="Wireless mouse",
            price=1000,
            category=self.category
        )

        self.store = Store.objects.create(
            name="Test Store",
            location="Mumbai"
        )

        self.inventory = Inventory.objects.create(
            store=self.store,
            product=self.product,
            quantity=10
        )

        self.inventory2 = Inventory.objects.create(
            store=self.store,
            product=self.product2,
            quantity=5
        )

    def test_inventory_listing(self):
        response = self.client.get(
            f"/stores/{self.store.id}/inventory/"
        )

        self.assertEqual(response.status_code, 200)

    def test_successful_order_creation(self):
        response = self.client.post(
            "/orders/",
            {
                "store_id": self.store.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity_requested": 2
                    }
                ]
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        order = Order.objects.latest("id")

        self.assertEqual(
            order.status,
            Order.Status.CONFIRMED
        )

    def test_insufficient_stock_rejects_order(self):
        response = self.client.post(
            "/orders/",
            {
                "store_id": self.store.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity_requested": 100
                    }
                ]
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        order = Order.objects.latest("id")

        self.assertEqual(
            order.status,
            Order.Status.REJECTED
        )

    def test_successful_order_deducts_inventory(self):
        self.client.post(
            "/orders/",
            {
                "store_id": self.store.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity_requested": 3
                    }
                ]
            },
            format="json"
        )

        self.inventory.refresh_from_db()

        self.assertEqual(
            self.inventory.quantity,
            7
        )

    def test_rejected_order_does_not_deduct_inventory(self):
        self.client.post(
            "/orders/",
            {
                "store_id": self.store.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity_requested": 100
                    }
                ]
            },
            format="json"
        )

        self.inventory.refresh_from_db()

        self.assertEqual(
            self.inventory.quantity,
            10
        )