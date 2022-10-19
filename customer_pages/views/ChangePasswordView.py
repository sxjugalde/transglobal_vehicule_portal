from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from ..forms.CustomerPasswordChangeForm import CustomerPasswordChangeForm


class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request):
        """Returns the change password screen."""
        context = {}
        context["page_name"] = "change_password"

        form = CustomerPasswordChangeForm(request.user)
        context["form"] = form

        return render(request, "customer_pages/change_password.html", context)

    def post(self, request):
        """Handles submission of the change password form."""
        context = {}
        context["page_name"] = "change_profile"

        form = CustomerPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")

            return redirect("home")
        else:
            messages.error(request, "Please correct the error below.")

        context["form"] = form

        return render(request, "customer_pages/change_password.html", context)
