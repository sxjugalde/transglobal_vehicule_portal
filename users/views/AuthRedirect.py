from django.shortcuts import redirect
from django.views.generic import View


class AuthRedirect(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        else:
            if request.user.is_staff or request.user.is_superuser:
                return redirect("admin:index")
            else:  # Customer user.
                return redirect("home")
