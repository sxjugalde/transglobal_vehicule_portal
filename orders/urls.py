from django.urls import path

from .views.UpsertCartRowsView import UpsertCartRowsView
from .views.DeleteCartRowsView import DeleteCartRowsView
from .views.SubmitOrderView import SubmitOrderView

urlpatterns = [
    path(
        "cartrow/upsert",
        UpsertCartRowsView.as_view(),
        name="orders_cartrow_upsert",
    ),
    path(
        "cartrow/delete",
        DeleteCartRowsView.as_view(),
        name="orders_cartrow_delete",
    ),
    path(
        "submit",
        SubmitOrderView.as_view(),
        name="orders_submit",
    ),
]
