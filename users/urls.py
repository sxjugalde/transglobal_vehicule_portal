from django.urls import path
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetConfirmView,
)

from .views.ConfirmAccount import ConfirmAccount
from .views.AuthRedirect import AuthRedirect
from .forms.CustomLoginForm import CustomLoginForm
from .forms.CustomPasswordResetForm import CustomPasswordResetForm
from .forms.CustomSetPasswordForm import CustomSetPasswordForm

urlpatterns = [
    path(
        "confirm-account/<uidb64>/<token>/",
        ConfirmAccount.as_view(),
        name="confirm-account",
    ),
    path(
        "auth-redirect",
        AuthRedirect.as_view(),
        name="auth-redirect",
    ),
    path(
        "login/",
        LoginView.as_view(
            authentication_form=CustomLoginForm,
        ),
        name="login",
    ),
    path(
        "password_reset/",
        PasswordResetView.as_view(
            form_class=CustomPasswordResetForm,
        ),
        name="password_reset",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            form_class=CustomSetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
]
