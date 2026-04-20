from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from supplier_app.models import Supplier
from supplier_app.serializers import SupplierBriefSerializer

from .models import Product
from .serializers import ProductSerializer, ProductSuppliersWriteSerializer


def _parse_path_bool(raw: str):
    """Map URL path segment to bool for is_active filters."""
    s = str(raw).strip().lower()
    if s in ("true", "1", "yes", "on"):
        return True
    if s in ("false", "0", "no", "off"):
        return False
    return None


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=["GET", "PUT", "PATCH"], url_path="suppliers")
    def manage_suppliers(self, request, pk=None):
        """
        List or change suppliers linked to this product (M2M via SupplierProduct).

        GET    /products/{id}/suppliers/ — current suppliers
        PUT    /products/{id}/suppliers/ — body {"supplier_ids": [uuid, ...]} replaces links
        PATCH  /products/{id}/suppliers/ — body {"supplier_ids": [uuid, ...]} adds links (merge)
        """
        product = self.get_object()

        # Handle mutating methods first so static analyzers do not treat the GET branch
        # as unreachable (DRF Request.method typing vs @action(methods=...)).
        if request.method != "GET":
            write = ProductSuppliersWriteSerializer(data=request.data)
            write.is_valid(raise_exception=True)
            supplier_ids = write.validated_data["supplier_ids"]

            suppliers = list(Supplier.objects.filter(pk__in=supplier_ids))
            found_ids = {s.pk for s in suppliers}
            missing = [str(x) for x in supplier_ids if x not in found_ids]
            if missing:
                return Response(
                    {"error": "Unknown supplier id(s).", "missing": missing},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if request.method == "PUT":
                product.supplier_products.set(suppliers)
            else:
                product.supplier_products.add(*suppliers)

            qs = product.supplier_products.order_by("name").all()
            return Response(SupplierBriefSerializer(qs, many=True).data)

        qs = product.supplier_products.order_by("name").all()
        return Response(SupplierBriefSerializer(qs, many=True).data)

    # Custom action to get products by category
    @action(detail=False, methods=["GET"], url_path="by-category")
    def by_category(self, request):
        category = request.query_params.get("category")
        if not category:
            return Response({"error": "Category is required"}, status=400)
        products = self.queryset.filter(category=category)
        if not products:
            return Response({"error": "No products found for this category"}, status=status.HTTP_204_NO_CONTENT)
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Custom action to get products by price range
    @action(detail=False, methods=["GET"])
    def by_price_range(self, request):
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        if not min_price or not max_price:
            return Response({"error": "Min price and max price are required"}, status=400)
        products = self.queryset.filter(unit_price__gte=min_price, unit_price__lte=max_price)
        if not products:
            return Response({"error": "No products found for this price range"}, status=status.HTTP_204_NO_CONTENT)
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # get products by active flag (path segment: true / false / 1 / 0)
    @action(
        detail=False,
        methods=["GET"],
        url_path=r"by_status/(?P<status_str>[^/.]+)",
    )
    def by_status(self, request, status_str):
        active = _parse_path_bool(status_str)
        if active is None:
            return Response(
                {"error": "status must be true or false (e.g. /products/by_status/true/)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        products = self.queryset.filter(is_active=active)
        if not products:
            return Response({"error": "No products found for this status"}, status=status.HTTP_204_NO_CONTENT)
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #update many products
    #update products prices (unit_price) by supplier id (passed as path parameter)
    #version 1 : with N+1 queries issue
    @action(detail=False, methods=["PUT"])
    def update_products_prices(self, request, supplier_id):
        products = self.queryset.filter(supplier_id=supplier_id)
        if not products:
            return Response({"error": "No products found for this supplier"}, status=status.HTTP_204_NO_CONTENT)
        for product in products:
            product.unit_price = request.data.get("unit_price")
            product.save()
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #version 2 : with bulk update
    @action(detail=False, methods=["PUT"])
    def update_products_prices(self, request, supplier_id):
        products = self.queryset.filter(supplier_id=supplier_id)
        if not products:
            return Response({"error": "No products found for this supplier"}, status=status.HTTP_204_NO_CONTENT)
        products.update(unit_price=request.data.get("unit_price"))
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #delete many products
    #delete production taht are perishable (expiry_date < today)
    @action(detail=False, methods=["DELETE"])
    def delete_perishable_products(self, request):
        products = self.queryset.filter(expiry_date__lt=timezone.now().date())
        if not products:
            return Response({"error": "No perishable products found"}, status=status.HTTP_204_NO_CONTENT)
        products.delete()
        return Response({"message": "Perishable products deleted successfully"}, status=status.HTTP_200_OK)