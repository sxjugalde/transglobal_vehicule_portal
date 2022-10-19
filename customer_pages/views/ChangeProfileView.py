from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from ..forms.ChangeProfileForm import ChangeProfileForm


class ChangeProfileView(LoginRequiredMixin, View):
    def get(self, request):
        """Returns the change profile screen."""
        context = {}
        context["page_name"] = "change_profile"

        form = ChangeProfileForm(user=request.user)
        context["form"] = form

        return render(request, "customer_pages/change_profile.html", context)

    def post(self, request):
        """Handles submission of the change profile form. Modifies user information."""
        context = {}
        context["page_name"] = "change_profile"

        form = ChangeProfileForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                form.save(request.user)
            except Exception:
                messages.error(
                    request,
                    "Please correct the error below.",
                )
            else:
                messages.success(request, "Your profile information was successfully updated!")

                return redirect("home")

        context["form"] = form

        return render(request, "customer_pages/change_profile.html", context)
