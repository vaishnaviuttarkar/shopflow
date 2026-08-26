from django.db import models

# Create your models here.
class Store(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    store = models.ForeignKey(
        Store, 
        on_delete=models.CASCADE,
        related_name="inventory"
    )
    product = models.ForeignKey(
        "products.Product", 
        on_delete=models.CASCADE,
        related_name="inventory_items"
    )
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ["store", "product"],
                name = "unique_store_product_inventory"
            )
        ]

    def __str__(self):
        return f"{self.store} - {self.product} ({self.quantity})"