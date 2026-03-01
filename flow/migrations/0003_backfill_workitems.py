from django.db import migrations

def backfill_workitems(apps, schema_editor):
    Order = apps.get_model("flow", "Order")
    WorkItem = apps.get_model("flow", "WorkItem")
    Workspace = apps.get_model("accounts", "Workspace")

    for order in Order.objects.all().iterator():
        # Resolve workspace from order creator (your current model)
        ws = Workspace.objects.filter(owner=order.created_by).first()
        if not ws:
            continue

        WorkItem.objects.get_or_create(
            order=order,
            defaults={
                "workspace": ws,
                "title": f"Order {order.order_number}",
                "status": order.status,
                "created_by": order.created_by,
            },
        )

class Migration(migrations.Migration):
    dependencies = [
        ("flow", "0002_workitem_workitemevent_and_more"),   # update this to your latest migration
        ("accounts", "0001_initial"), # adjust if needed
    ]

    operations = [
        migrations.RunPython(backfill_workitems, migrations.RunPython.noop),
    ]