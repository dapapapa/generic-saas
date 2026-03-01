from django.urls import path

from . import views


urlpatterns = [
    # Board
    path("board/", views.flow_board, name="flow-board"),

    # Existing order move (keep working)
    path(
        "orders/<int:order_id>/move/<str:new_status>/",
        views.move_order_status,
        name="flow-move-order",
    ),

    # New: work item move
    path(
        "workitems/<int:item_id>/move/<str:new_status>/",
        views.move_work_item_status,
        name="flow-move-workitem",
    ),
]
