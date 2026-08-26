from django.core.management.base import BaseCommand
from faker import Faker

from products.models import Category, Product
from stores.models import Store, Inventory


class Command(BaseCommand):
    help = "Generate dummy categories, products, stores and inventory."

    def handle(self, *args, **options):

        fake = Faker()

        self.stdout.write(
            self.style.WARNING(
                "Generating seed data..."
            )
        )

        # -------------------------
        # Categories
        # -------------------------

        category_names = [
            "Electronics",
            "Clothing",
            "Home & Kitchen",
            "Books",
            "Sports",
            "Beauty",
            "Toys",
            "Grocery",
            "Furniture",
            "Automotive",
            "Footwear",
            "Jewelry",
            "Stationery",
            "Garden",
            "Pet Supplies",
        ]

        categories = [
            Category(name=name)
            for name in category_names
        ]

        Category.objects.bulk_create(
            categories,
            ignore_conflicts=True,
        )

        categories = list(
            Category.objects.all()
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(categories)} categories."
            )
        )

        # -------------------------
        # Products
        # -------------------------

        products = []

        for index in range(1000):

            products.append(
                Product(
                    title=(
                        f"{fake.catch_phrase()} "
                        f"Product {index + 1}"
                    ),
                    description=fake.text(
                        max_nb_chars=200
                    ),
                    price=fake.pydecimal(
                        left_digits=4,
                        right_digits=2,
                        positive=True,
                    ),
                    category=fake.random_element(
                        categories
                    ),
                )
            )

        Product.objects.bulk_create(
            products,
            batch_size=500,
        )

        products = list(
            Product.objects.all()
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(products)} products."
            )
        )

        # -------------------------
        # Stores
        # -------------------------

        stores = []

        for index in range(20):

            stores.append(
                Store(
                    name=f"Store {index + 1}",
                    location=fake.city(),
                )
            )

        Store.objects.bulk_create(
            stores,
            batch_size=20,
        )

        stores = list(
            Store.objects.all()
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(stores)} stores."
            )
        )

        # -------------------------
        # Inventory
        # -------------------------

        inventory_records = []

        for store in stores:

            selected_products = fake.random_elements(
                elements=products,
                length=300,
                unique=True,
            )

            for product in selected_products:

                inventory_records.append(
                    Inventory(
                        store=store,
                        product=product,
                        quantity=fake.random_int(
                            min=0,
                            max=100,
                        ),
                    )
                )

        Inventory.objects.bulk_create(
            inventory_records,
            batch_size=1000,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(inventory_records)} inventory records."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Seed data generation completed."
            )
        )