from django.urls import include, path
from rest_framework.routers import DefaultRouter

from distribution_app.views import (
    DistributionCenterViewSet,
    ShipmentItemViewSet,
    ShipmentViewSet,
)
from order_app.views import PurchaseOrderItemViewSet, PurchaseOrderViewSet
from product_app.views import ProductViewSet
from supplier_app.views import SupplierViewSet
from warehouse_app.views import InventoryViewSet, WarehouseViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"suppliers", SupplierViewSet, basename="supplier")
router.register(r"purchase-orders", PurchaseOrderViewSet, basename="purchase-order")
router.register(
    r"purchase-order-items",
    PurchaseOrderItemViewSet,
    basename="purchase-order-item",
)
router.register(r"warehouses", WarehouseViewSet, basename="warehouse")
router.register(r"inventory", InventoryViewSet, basename="inventory")
router.register(
    r"distribution-centers",
    DistributionCenterViewSet,
    basename="distribution-center",
)
router.register(r"shipments", ShipmentViewSet, basename="shipment")
router.register(r"shipment-items", ShipmentItemViewSet, basename="shipment-item")

urlpatterns = [path("", include(router.urls))]
