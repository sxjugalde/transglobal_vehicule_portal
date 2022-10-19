from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import send_mail, mail_managers
from django.contrib import messages


def send_quote_request_submitted_email(request, order):
    current_site = get_current_site(request)
    subject = f"New quote request submitted by {order.company_name}!"
    html_message = render_to_string(
        "emails/quote_request_submitted_email.html",
        {
            "order": order,
            "domain": current_site.domain,
        },
    )
    mail_managers(
        subject=subject,
        message=html_message,
        fail_silently=False,
        html_message=html_message,
    )


def send_quote_request_reviewed_email(request, user_username, user_email, order_id):
    current_site = get_current_site(request)
    subject = "[Transglobal] Quote request reviewed!"
    html_message = render_to_string(
        "emails/quote_request_reviewed_email.html",
        {
            "user_username": user_username,
            "order_id": order_id,
            "domain": current_site.domain,
        },
    )
    try:
        send_mail(
            subject=subject,
            message=html_message,
            from_email=None,
            recipient_list=[user_email],
            fail_silently=False,
            html_message=html_message,
        )
        messages.success(
            request,
            (
                "An email has been sent to the user to notify them that the order has changed status."
            ),
        )
    except Exception as e:
        messages.warning(
            request,
            (
                "There was an error while delivering the order reviewed notification email to the user."
            ),
        )
