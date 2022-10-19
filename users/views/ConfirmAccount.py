from django.views import View
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import User
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.tokens import default_token_generator

from ..logic.AccountActivationTokenGenerator import account_activation_token


class ConfirmAccount(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user_model = get_user_model()
            user = user_model.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.email_confirmed = True
            user.save()
            messages.success(
                request,
                (
                    "Thank you! Your account has been confirmed, please proceed to set your new password."
                ),
            )

            # Create auxiliary parameters for SetPassword view.
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            return redirect("password_reset_confirm", uidb64=uid, token=token)
        else:
            messages.warning(
                request,
                (
                    "The confirmation link was invalid, possibly because it has already been used. If required, please contact a system administrator for support."
                ),
            )
            return redirect("login")
