from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models import Workspace


User = get_user_model()

class SKU(models.Model):
    sku_code = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255, blank=True)
    packs_per_pallet = models.PositiveIntegerField()

    def __str__(self):
        return self.sku_code


class Order(models.Model):
    class Status(models.TextChoices):
        RELEASED = "released", "Released"
        BULK = "bulk", "Bulk Pick"
        FORWARD = "forward", "Forward Pick"
        VERIFY = "verify", "Verify"
        READY = "ready", "Ready"
        EXCEPTION = "exception", "Exception"
        DISPATCHED = "dispatched", "Dispatched"

    order_number = models.CharField(max_length=64, unique=True)
    customer_name = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RELEASED)

    cutoff_at = models.DateTimeField(null=True, blank=True)     # later: auto 3pm
    dispatch_at = models.DateTimeField(null=True, blank=True)   # later: auto 8am next day

    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_number


class OrderLine(models.Model):
    order = models.ForeignKey(Order, related_name="lines", on_delete=models.CASCADE)
    sku = models.ForeignKey(SKU, on_delete=models.PROTECT)
    required_packs = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.order.order_number} - {self.sku.sku_code}"
    
class WorkItem(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="work_items")

    # Optional link to your existing Order, so you can phase it in
    order = models.OneToOneField("flow.Order", on_delete=models.SET_NULL, null=True, blank=True, related_name="work_item")

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Reuse your existing status values.
    status = models.CharField(max_length=32, default="released", db_index=True)

    priority = models.PositiveSmallIntegerField(default=3)  # 1=high, 5=low
    due_at = models.DateField(null=True, blank=True)

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_work_items",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_work_items",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    entered_status_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["workspace", "status"]),
            models.Index(fields=["workspace", "created_at"]),
        ]

    def __str__(self):
        return self.title


class WorkItemEvent(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="work_item_events")
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name="events")

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_item_events",
    )

    event_type = models.CharField(max_length=32)  # created, moved, assigned, note, etc.
    from_status = models.CharField(max_length=32, blank=True)
    to_status = models.CharField(max_length=32, blank=True)
    message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "created_at"]),
            models.Index(fields=["work_item", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} {self.work_item_id}"
