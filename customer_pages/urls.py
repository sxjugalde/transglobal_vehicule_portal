from django.urls import path

from .views.HomeView import HomeView
from .views.VehicleDetailsView import VehicleDetailsView
from .views.ShoppingCartView import ShoppingCartView
from .views.ChangeProfileView import ChangeProfileView
from .views.ChangePasswordView import ChangePasswordView
from .views.PreviousOrdersListView import PreviousOrdersListView
from .views.OrderDetailsView import OrderDetailsView

urlpatterns = [
    path(
        "",
        HomeView.as_view(),
        name="home",
    ),
    path(
        "vehicle/<str:vin>",
        VehicleDetailsView.as_view(),
        name="vehicle_details",
    ),
    path(
        "cart",
        ShoppingCartView.as_view(),
        name="shopping_cart",
    ),
    path(
        "profile_change",
        ChangeProfileView.as_view(),
        name="profile_change",
    ),
    path(
        "password_change",
        ChangePasswordView.as_view(),
        name="password_change",
    ),
    path(
        "previous_orders",
        PreviousOrdersListView.as_view(),
        name="previous_orders",
    ),
    path(
        "order/<int:order_id>",
        OrderDetailsView.as_view(),
        name="order_details",
    ),
]
