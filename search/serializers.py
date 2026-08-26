from rest_framework import serializers

from products.models import Product

from decimal import Decimal

class ProductSearchParamsSerializer(serializers.Serializer):
    q = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    category = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    min_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0"),
    )

    max_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0"),
    )

    store_id = serializers.IntegerField(
        required=False,
        min_value=1,
    )

    in_stock = serializers.BooleanField(
        required=False,
    )

    sort = serializers.ChoiceField(
        required=False,
        choices=[
            "price",
            "newest",
            "relevance",
        ],
    )

    def validate(self, attrs):
        min_price = attrs.get("min_price")
        max_price = attrs.get("max_price")

        if (
            min_price is not None
            and max_price is not None
            and min_price > max_price
        ):
            raise serializers.ValidationError(
                "min_price cannot be greater than max_price."
            )

        if (
            attrs.get("sort") == "relevance"
            and not attrs.get("q")
        ):
            raise serializers.ValidationError(
                "q is required when sort=relevance."
            )

        return attrs
    
class ProductSearchSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    inventory_quantity = serializers.IntegerField(
        read_only=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "category_name",
            "created_at",
            "inventory_quantity",
        ]
