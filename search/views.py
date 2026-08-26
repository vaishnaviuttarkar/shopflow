from django.db.models import (
    Case,
    IntegerField,
    Q,
    Value,
    When,
    F, 
    OuterRef, 
    Subquery,
)

from products.models import Product
from stores.models import Inventory

from .serializers import (
    ProductSearchParamsSerializer,
    ProductSearchSerializer,
)

from .pagination import ProductSearchPagination

from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

class ProductSearchView(ListAPIView):
    serializer_class = ProductSearchSerializer
    pagination_class = ProductSearchPagination

    def get_queryset(self):
        queryset = Product.objects.select_related(
            "category"
        )

        params_serializer = ProductSearchParamsSerializer(
            data=self.request.query_params
        )

        params_serializer.is_valid(raise_exception=True)

        params = params_serializer.validated_data

        query = params.get("q")
        category = params.get("category")
        min_price = params.get("min_price")
        max_price = params.get("max_price")
        store_id = params.get("store_id")
        in_stock = params.get("in_stock")
        sort = params.get("sort")

        # Keyword search
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(category__name__icontains=query)
            )

        # Category filter
        if category:
            queryset = queryset.filter(
                category__name__iexact=category
            )

        # Price filter
        if min_price:
            queryset = queryset.filter(
                price__gte=min_price
            )

        if max_price:
            queryset = queryset.filter(
                price__lte=max_price
            )

        # Store filter
        if store_id:
            queryset = queryset.filter(
                inventory_items__store_id=store_id
            )

            inventory_quantity = Inventory.objects.filter(
                store_id=store_id,
                product_id=OuterRef("pk"),
            ).values("quantity")[:1]

            queryset = queryset.annotate(
                inventory_quantity=Subquery(
                    inventory_quantity
                )
            )

        # Stock filter
        if store_id and in_stock is not None:

            if in_stock:
                queryset = queryset.filter(
                    inventory_items__store_id=store_id,
                    inventory_items__quantity__gt=0,
                )

            else:
                queryset = queryset.filter(
                    inventory_items__store_id=store_id,
                    inventory_items__quantity=0,
                )
                        
        # Sorting
        if sort == "price":
            queryset = queryset.order_by("price")
        elif sort == "newest":
            queryset = queryset.order_by("-created_at")
        elif sort == "relevance" and query:
            queryset = queryset.annotate(
                relevance=Case(
                    When(
                        title__iexact=query,
                        then=Value(4),
                    ),
                    When(
                        title__istartswith=query,
                        then=Value(3),
                    ),
                    When(
                        title__icontains=query,
                        then=Value(2),
                    ),
                    When(
                        description__icontains=query,
                        then=Value(1),
                    ),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ).order_by("-relevance", "title")
        else:
            queryset = queryset.order_by("title")

        return queryset

class ProductSuggestView(APIView):

    def get(self, request):

        query = request.query_params.get("q", "").strip()

        if len(query) < 3:
            return Response(
                {
                    "error": "q must contain at least 3 characters."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        products = (
            Product.objects
            .filter(title__icontains=query)
            .annotate(
                match_priority=Case(
                    When(
                        title__istartswith=query,
                        then=Value(0),
                    ),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by(
                "match_priority",
                "title",
            )[:10]
        )

        return Response({
            "results": [
                product.title
                for product in products
            ]
        })