from django.db import migrations


class Migration(migrations.Migration):
    """Remove relocated models from product_app state only; tables are unchanged."""

    dependencies = [
        ("product_app", "0006_supply_chain_models"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name="ShipmentItem"),
                migrations.DeleteModel(name="Shipment"),
                migrations.DeleteModel(name="DistributionCenter"),
                migrations.DeleteModel(name="Inventory"),
                migrations.DeleteModel(name="Warehouse"),
                migrations.DeleteModel(name="PurchaseOrderItem"),
                migrations.DeleteModel(name="PurchaseOrder"),
                migrations.DeleteModel(name="Supplier"),
            ],
            database_operations=[],
        ),
    ]
