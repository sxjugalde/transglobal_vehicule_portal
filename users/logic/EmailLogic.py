from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages

from .AccountActivationTokenGenerator import account_activation_token


def send_account_confirmation_email(request, user):
    current_site = get_current_site(request)
    subject = "[Transglobal] New account created!"
    html_message = render_to_string(
        "emails/confirmation_email.html",
        {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        },
    )
    try:
        send_mail(
            subject=subject,
            message=html_message,
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_message,
        )
        user.confirmation_email_sent = True
        user.save()
        messages.success(
            request,
            ("An email has been sent to the user to complete registration."),
        )
    except Exception as e:
        messages.warning(
            request,
            ("There was an error while delivering the confirmation email to the user."),
        )
