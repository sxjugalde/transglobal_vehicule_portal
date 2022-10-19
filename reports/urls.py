from django.urls import path

from .views.MostRequestedPartsReportView import MostRequestedPartsReportView

urlpatterns = [
    path(
        "most_requested_parts",
        MostRequestedPartsReportView.as_view(),
        name="reports_most_requested_parts",
    ),
]
