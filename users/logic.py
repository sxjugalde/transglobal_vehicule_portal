from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import Group
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages


# Account confirmation token gen
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.email_confirmed}"


account_activation_token = AccountActivationTokenGenerator()


# Emails
def send_account_confirmation_email(request, user):
    current_site = get_current_site(request)
    subject = "Transglobal: New account created!"
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


# User groups
def auto_assign_groups(
    user, staff_group_name: str = "Staff", customer_group_name: str = "Customer"
):
    groups = user.groups.all()
    belongs_to_staff = groups.filter(name=staff_group_name).exists()
    # belongs_to_customer = groups.filter(name=customer_group_name).exists()
    staff_group = Group.objects.get(name=staff_group_name)
    # customer_group = Group.objects.get(name=customer_group_name)

    if user.is_staff:
        if not belongs_to_staff:
            user.groups.add(staff_group)

        # if belongs_to_customer: # Delete wrong group.
        # self.groups.remove(customer_group)
    elif not user.is_staff:  # Delete wrong group.
        if belongs_to_staff:
            user.groups.remove(staff_group)

        # if not belongs_to_customer: # It's a new customer.
        #     self.groups.add(customer_group)
    user.save()
