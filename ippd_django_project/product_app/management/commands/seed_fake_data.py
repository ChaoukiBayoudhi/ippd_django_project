"""
Load demo rows into every app model (at least 5 instances each).

Usage (from the folder that contains manage.py):

    python manage.py seed_fake_data
"""

import uuid
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from distribution_app.models import DistributionCenter, Shipment, ShipmentItem
from order_app.models import PurchaseOrder, PurchaseOrderItem
from product_app.models import Product
from supplier_app.models import Supplier, SupplierProduct
from warehouse_app.models import Inventory, Warehouse


COUNT = 5


class Command(BaseCommand):
    help = "Insert at least five fake rows per model (respects validators and FK order)."

    def handle(self, *args, **options):
        # Unique per invocation so reruns do not hit UNIQUE on (name, photo), sku, codes, etc.
        run_id = uuid.uuid4().hex[:8]
        today = timezone.now().date()
        mfg = today - timedelta(days=30)
        expiry = today + timedelta(days=180)
        phone_base = abs(hash(run_id)) % 100_000_000

        with transaction.atomic():
            products = []
            for i in range(COUNT):
                p = Product.objects.create(
                    sku=f"SEED-{run_id}-SKU-{i + 1:02d}",
                    name=f"Seed product {run_id} {i + 1}",
                    description=f"Demo description for catalog item {i + 1}.",
                    unit_price=Decimal("10.00") + Decimal(i),
                    category=["Beverage", "Dairy", "Dry", "Frozen", "Produce"][i % 5],
                    is_active=True,
                    manufactured_date=mfg,
                    expiry_date=expiry,
                )
                products.append(p)

            suppliers = []
            for i in range(COUNT):
                s = Supplier.objects.create(
                    name=f"Seed supplier {run_id} {i + 1}",
                    code=f"SEED-{run_id}-SUP-{i + 1:02d}",
                    email=f"seed-{run_id}-sup-{i + 1:02d}@example.com",
                    phone=f"+216{(phone_base + i) % 100_000_000:08d}",
                    address=f"{100 + i} Rue de Demo, Tunis",
                    is_active=True,
                    rating=Decimal(str(3 + (i % 3))),
                )
                suppliers.append(s)

            for i in range(COUNT):
                SupplierProduct.objects.create(
                    supplier=suppliers[i],
                    product=products[i],
                )

            warehouses = []
            for i in range(COUNT):
                w = Warehouse.objects.create(
                    code=f"SEED-{run_id}-WH-{i + 1:02d}",
                    name=f"Seed warehouse {run_id} {i + 1}",
                    location=f"Zone {i + 1}, Industrial Park",
                    capacity_sqft=Decimal("5000.00") + Decimal(i * 100),
                    is_active=True,
                )
                warehouses.append(w)

            inventories = []
            for i in range(COUNT):
                inv = Inventory.objects.create(
                    warehouse=warehouses[i],
                    product=products[i],
                    quantity_on_hand=500,
                    reorder_point=50,
                    max_stock_level=1000,
                )
                inventories.append(inv)

            distribution_centers = []
            for i in range(COUNT):
                dc = DistributionCenter.objects.create(
                    code=f"SEED-{run_id}-DC-{i + 1:02d}",
                    name=f"Seed distribution center {run_id} {i + 1}",
                    location=f"Hub {i + 1}, Coastal region",
                    service_region=f"Region-{i + 1}",
                    is_active=True,
                )
                distribution_centers.append(dc)

            purchase_orders = []
            for i in range(COUNT):
                order_date = today - timedelta(days=10 - i)
                expected = order_date + timedelta(days=14)
                po = PurchaseOrder.objects.create(
                    order_number=f"SEED-{run_id}-PO-{i + 1:04d}",
                    supplier=suppliers[i],
                    order_date=order_date,
                    expected_delivery_date=expected,
                    status=PurchaseOrder.Status.SUBMITTED,
                    total_amount=Decimal("0"),
                )
                PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    product=products[i],
                    quantity=5 + i,
                    unit_price=products[i].unit_price,
                )
                po.total_amount = po.calculate_total()
                po.save()
                purchase_orders.append(po)

            shipments = []
            for i in range(COUNT):
                ship_date = today - timedelta(days=5 - i)
                arrival = ship_date + timedelta(days=3)
                sh = Shipment.objects.create(
                    shipment_number=f"SEED-{run_id}-SH-{i + 1:04d}",
                    warehouse=warehouses[i],
                    distribution_center=distribution_centers[i],
                    ship_date=ship_date,
                    expected_arrival_date=arrival,
                    status=Shipment.Status.IN_TRANSIT,
                    carrier=f"Seed carrier {i + 1}",
                )
                shipments.append(sh)

            shipment_items = []
            for i in range(COUNT):
                si = ShipmentItem.objects.create(
                    shipment=shipments[i],
                    product=products[i],
                    quantity=10 + i,
                )
                shipment_items.append(si)

        self.stdout.write(
            self.style.SUCCESS(
                f"Run id {run_id}: created {COUNT} rows per model: "
                f"{len(products)} products, {len(suppliers)} suppliers, "
                f"{COUNT} supplier-product links, {len(warehouses)} warehouses, "
                f"{len(inventories)} inventory rows, {len(distribution_centers)} DCs, "
                f"{len(purchase_orders)} purchase orders (+ line items), "
                f"{len(shipments)} shipments (+ line items)."
            )
        )
