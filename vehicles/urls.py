from django.urls import path

from .views.SearchCompanyVehiclesView import SearchCompanyVehiclesView
from .views.ChangeVehicleView import ChangeVehicleView

urlpatterns = [
    path(
        "search",
        SearchCompanyVehiclesView.as_view(),
        name="vehicles_search",
    ),
    path(
        "vehicle/<int:vehicle_id>/change/",
        ChangeVehicleView.as_view(),
        name="vehicles_vehicle_change",
    ),
]
