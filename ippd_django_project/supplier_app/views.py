from collections import defaultdict

from django.db.models import Avg, Count, Max, Min, Q, Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Supplier, SupplierProduct
from .serializers import SupplierProductSerializer, SupplierSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().prefetch_related("products")
    serializer_class = SupplierSerializer

    @action(detail=False, methods=["GET"], url_path="product-statistics")
    def product_statistics(self, request):
        """
        Aggregated product stats per supplier (linked via SupplierProduct).

        GET /suppliers/product-statistics/
        """
        rows = (
            Supplier.objects.annotate(
                product_count=Count("products", distinct=True),
                active_product_count=Count(
                    "products",
                    filter=Q(products__is_active=True),
                    distinct=True,
                ),
                inactive_product_count=Count(
                    "products",
                    filter=Q(products__is_active=False),
                    distinct=True,
                ),
                avg_unit_price=Avg("products__unit_price"),
            )
            .values(
                "id",
                "name",
                "code",
                "is_active",
                "product_count",
                "active_product_count",
                "inactive_product_count",
                "avg_unit_price",
            )
            .order_by("name")
        )
        return Response(list(rows))

    @action(detail=False, methods=["GET"], url_path="advanced-product-statistics")
    def advanced_product_statistics(self, request):
        """
        Richer analytics: price min/max/sum, distinct categories, and per-category counts.

        GET /suppliers/advanced-product-statistics/
        Query params:
          - supplier_id (optional): limit to one supplier UUID
        """
        supplier_id = request.query_params.get("supplier_id")
        base = Supplier.objects.all()
        if supplier_id:
            base = base.filter(pk=supplier_id)

        annotated = (
            base.annotate(
                product_count=Count("products", distinct=True),
                active_product_count=Count(
                    "products",
                    filter=Q(products__is_active=True),
                    distinct=True,
                ),
                inactive_product_count=Count(
                    "products",
                    filter=Q(products__is_active=False),
                    distinct=True,
                ),
                avg_unit_price=Avg("products__unit_price"),
                min_unit_price=Min("products__unit_price"),
                max_unit_price=Max("products__unit_price"),
                sum_unit_price=Sum("products__unit_price"),
                distinct_category_count=Count("products__category", distinct=True),
            )
            .values(
                "id",
                "name",
                "code",
                "is_active",
                "product_count",
                "active_product_count",
                "inactive_product_count",
                "avg_unit_price",
                "min_unit_price",
                "max_unit_price",
                "sum_unit_price",
                "distinct_category_count",
            )
            .order_by("name")
        )
        suppliers_payload = list(annotated)
        id_list = [row["id"] for row in suppliers_payload]

        by_supplier_category = defaultdict(list)
        if id_list:
            cat_qs = (
                SupplierProduct.objects.filter(supplier_id__in=id_list)
                .values("supplier_id", "product__category")
                .annotate(product_count=Count("id"))
                .order_by("supplier_id", "product__category")
            )
            for row in cat_qs:
                by_supplier_category[row["supplier_id"]].append(
                    {
                        "category": row["product__category"],
                        "product_count": row["product_count"],
                    }
                )

        for row in suppliers_payload:
            sid = row["id"]
            row["by_category"] = by_supplier_category.get(sid, [])
            row["totals"] = {
                "product_count": row.pop("product_count"),
                "active_product_count": row.pop("active_product_count"),
                "inactive_product_count": row.pop("inactive_product_count"),
                "avg_unit_price": row.pop("avg_unit_price"),
                "min_unit_price": row.pop("min_unit_price"),
                "max_unit_price": row.pop("max_unit_price"),
                "sum_unit_price": row.pop("sum_unit_price"),
                "distinct_category_count": row.pop("distinct_category_count"),
            }

        total_linked = sum(t["totals"]["product_count"] for t in suppliers_payload)

        return Response(
            {
                "suppliers": suppliers_payload,
                "summary": {
                    "supplier_count": len(suppliers_payload),
                    "total_product_links": total_linked,
                },
            }
        )


class SupplierProductViewSet(viewsets.ModelViewSet):
    queryset = SupplierProduct.objects.all()
    serializer_class = SupplierProductSerializer
