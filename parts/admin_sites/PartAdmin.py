from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.http import HttpResponseRedirect
from django.urls import re_path as url
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.urls import reverse

from .PartSupplierInline import PartSupplierInline
from ..models.Part import Part
from ..models.PartSupplier import PartSupplier
from ..forms.PartActionForm import ReplaceActionForm
from utils.mixins.AuditableMixin import AuditableMixin


@admin.register(Part)
class PartAdmin(AuditableMixin, admin.ModelAdmin):

    actions = None
    save_as = True
    fields = [
        "name",
        "code",
        "suffix",
        "revision",
        "notes",
        "dimension",
        "material",
        "is_purchased",
        "is_obsolete",
    ]
    list_display = (
        "name",
        "code",
        "suffix",
        "revision",
        "notes",
        "is_purchased",
        "is_obsolete",
        "modified_on",
        "part_actions",
    )
    list_filter = ["is_purchased", "is_obsolete", "modified_on"]
    search_fields = ["full_code", "name"]
    inlines = (PartSupplierInline,)
    formfield_overrides = {
        models.TextField: {
            "widget": Textarea(
                attrs={
                    "rows": 2,
                    "cols": 80,
                }
            )
        },
    }

    def part_actions(self, obj):
        return format_html(
            '<a class="button" href="{}" title="Replace" aria-label="Replace"><i class="fa fa-exchange" aria-hidden="true"></i></a>&nbsp;',
            # '<a class="button" style="background-color: #DD4646" href="{}" title="Delete" aria-label="Delete"><i class="fa fa-times" aria-hidden="true"></i></a>',
            reverse("admin:parts_part_replace", args=[obj.pk]),
            # reverse("admin:parts_part_delete", args=[obj.pk]),
        )

    part_actions.short_description = "Actions"
    part_actions.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r"^(?P<part_id>.+)/replace/$",
                self.admin_site.admin_view(self.process_replace),
                name="parts_part_replace",
            ),
        ]
        return custom_urls + urls

    def process_replace(self, request, part_id, *args, **kwargs):
        part = self.get_object(request, part_id)
        if request.method != "POST":
            form = ReplaceActionForm(part=part)
        else:
            form = ReplaceActionForm(request.POST, part=part)
            if form.is_valid():
                try:
                    form.save(part, request.user)
                except Exception:
                    pass
                else:
                    self.message_user(
                        request, f"Part {part.name} replaced successfully."
                    )
                    url = reverse(
                        "admin:parts_part_changelist",
                        current_app=self.admin_site.name,
                    )
                    return HttpResponseRedirect(url)
        context = self.admin_site.each_context(request)
        context["opts"] = self.model._meta
        context["form"] = form
        context["part"] = part
        context["no_integrations"] = form.no_integrations
        context["title"] = f"[{part.full_code}] Replace {part.name}"
        return TemplateResponse(
            request,
            "admin/parts_action_replace.html",
            context,
        )
