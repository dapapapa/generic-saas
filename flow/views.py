from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Workspace
from .models import Order, WorkItem
from .rules import ALLOWED_TRANSITIONS, WIP_LIMITS
from .services import InvalidTransition, move_work_item


def _get_workspace(request):
    """
    Single place to resolve the current workspace.
    Your current SaaS uses 1 workspace per owner via signals.
    """
    return get_object_or_404(Workspace, owner=request.user)


@login_required
def flow_board(request):
    ws = _get_workspace(request)

    # Keep your existing columns list if you already have it.
    # Otherwise this matches the statuses in your rules.
    columns = [
        ("released", "Released"),
        ("bulk", "Bulk Pick"),
        ("ready", "Ready"),
        ("packed", "Packed"),
        ("shipped", "Shipped"),
        ("exception", "Exception"),
    ]

    items = (
        WorkItem.objects.filter(workspace=ws)
        .select_related("assignee", "order")
        .order_by("-updated_at")
    )

    items_by_status = {k: [] for k, _ in columns}
    for item in items:
        items_by_status.setdefault(item.status, []).append(item)

    ui_helpers = {}
    for item in items:
        allowed = ALLOWED_TRANSITIONS.get(item.status, [])
        ui_helpers[item.id] = {
            "next_status": allowed[0] if allowed else None,
            "can_exception": item.status != "exception",
        }

    return render(
        request,
        "flow/board.html",
        {
            "columns": columns,
            "items_by_status": items_by_status,
            "ui_helpers": ui_helpers,
            "wip_limits": WIP_LIMITS,
        },
    )


@require_POST
@login_required
def move_work_item_status(request, item_id: int, new_status: str):
    ws = _get_workspace(request)
    item = get_object_or_404(WorkItem, id=item_id, workspace=ws)

    try:
        move_work_item(work_item=item, to_status=new_status, actor=request.user)
        messages.success(request, f"Moved to {new_status}.")
    except InvalidTransition:
        messages.error(request, "That move isn't allowed.")

    return redirect("flow-board")


# ---------------------------
# Existing order move (keep it)
# ---------------------------


@require_POST
@login_required
def move_order_status(request, order_id: int, new_status: str):
    """
    Keep your existing order move logic.
    This version is a safe baseline: owner isolation + transition validation.
    If you already have this implemented, keep yours.
    """
    order = get_object_or_404(Order, id=order_id, created_by=request.user)

    allowed = ALLOWED_TRANSITIONS.get(order.status, [])
    if new_status not in allowed:
        messages.error(request, "That move isn't allowed.")
        return redirect("flow-board")

    order.status = new_status
    order.save(update_fields=["status"])
    messages.success(request, f"Order moved to {new_status}.")
    return redirect("flow-board")
