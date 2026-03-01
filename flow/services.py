from django.utils import timezone
from .models import WorkItem, WorkItemEvent
from .rules import ALLOWED_TRANSITIONS, WIP_LIMITS


class InvalidTransition(Exception):
    pass


def move_work_item(*, work_item: WorkItem, to_status: str, actor) -> WorkItem:
    from_status = work_item.status
    allowed = ALLOWED_TRANSITIONS.get(from_status, [])
    if to_status not in allowed:
        raise InvalidTransition(f"{from_status} -> {to_status} not allowed")

    # 🔒 WIP enforcement
    limit = WIP_LIMITS.get(to_status)
    if limit is not None:
        current_count = WorkItem.objects.filter(
            workspace=work_item.workspace,
            status=to_status,
        ).count()

        if current_count >= limit:
            raise InvalidTransition(
                f"WIP limit reached for {to_status} ({current_count}/{limit})"
            )

    work_item.status = to_status
    work_item.entered_status_at = timezone.now()
    work_item.save(update_fields=["status", "entered_status_at", "updated_at"])

    WorkItemEvent.objects.create(
        workspace=work_item.workspace,
        work_item=work_item,
        actor=actor,
        event_type="moved",
        from_status=from_status,
        to_status=to_status,
    )

    return work_item
