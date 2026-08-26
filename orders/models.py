from django.db import models

# Create your models here.
class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "pending"
        CONFIRMED = "CONFIRMED", "confirmed"
        REJECTED = "REJECTED", "rejected"

    store = models.ForeignKey(
        "stores.Store",
        on_delete = models.CASCADE,
        related_name="orders"
    )
    status = models.CharField(
        max_length=20,
        choices = Status.choices,
        default = Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete = models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete = models.CASCADE,
        related_name="order_items"
    )
    quantity_requested = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.product} x {self.quantity_requested}"