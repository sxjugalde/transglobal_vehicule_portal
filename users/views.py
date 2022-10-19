from django.views import View
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
from django.shortcuts import redirect

from .logic import account_activation_token


class ConfirmAccount(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user_model = get_user_model()
            user = user_model.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        link_invalid = False
        if user is not None and account_activation_token.check_token(user, token):
            user.email_confirmed = True
            user.save()
            login(request, user)
        else:
            link_invalid = True
            messages.warning(
                request,
                (
                    "The confirmation link was invalid, possibly because it has already been used. If required, please contact a system administrator for support."
                ),
            )

        if user.is_staff or user.is_superuser:
            if not link_invalid:
                messages.success(
                    request,
                    (
                        "Your account have been confirmed. Welcome to the administrative portal!"
                    ),
                )
            return redirect("admin:index")
        else:
            if not link_invalid:
                messages.success(
                    request,
                    (
                        "Your account have been confirmed. Welcome to the customer portal!"
                    ),
                )
            # TODO: Replace with correct redirect.
            return redirect("admin:index")
