from datetime import datetime

from django.contrib import admin, messages
from django.views.generic import View
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.template.loader import get_template
from django.http import HttpResponse

from xhtml2pdf import pisa

from utils.logic.link_callback import link_callback
from orders.models.Order import Order
from orders.logic.CartLogic import get_most_requested_items
from ..forms.MostRequestedPartsReportForm import MostRequestedPartsReportForm


class MostRequestedPartsReportView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "orders.view_order"

    def get(self, request):
        """Returns the form required to generate the report."""
        context = admin.site.each_context(request)
        context["title"] = "Report - Most Requested Parts"
        form = MostRequestedPartsReportForm()
        form.load_bom_choices()
        context["form"] = form

        return render(request, "admin/reports_most_requested_parts.html", context)

    def post(self, request):
        """Generates the report based on the form's input and redirects."""
        context = admin.site.each_context(request)
        context["title"] = "Report - Most Requested Parts"

        form = MostRequestedPartsReportForm(request.POST)
        form.load_bom_choices()
        if form.is_valid():
            try:
                from_date = form.cleaned_data["from_date"]
                to_date = form.cleaned_data["to_date"]
                count = form.cleaned_data["count"]
                bom = form.cleaned_data["bom"]
                context["report_parameters"] = {
                    "from_date": from_date,
                    "to_date": to_date,
                    "count": count,
                    "bom": dict(form.fields["bom"].choices)[int(bom)] if bom else None,
                }
                context["report_items"] = get_most_requested_items(
                    from_date=from_date, to_date=to_date, count=count, bom_id=bom
                )

                search_report = "search_report" in request.POST  # Unused.
                print_report = "print_report" in request.POST

                # Create PDF file quickly from base HTML
                if print_report:
                    # Create a Django response object, and specify content_type as pdf
                    file_name = f"TG_MostRequestedParts_{from_date}_{to_date}.pdf"
                    context["title"] = "REPORT - MOST REQUESTED PARTS"
                    context["current_date"] = datetime.today().strftime("%Y-%m-%d")
                    context["print_pdf"] = True
                    response = HttpResponse(content_type="application/pdf")
                    response[
                        "Content-Disposition"
                    ] = f'attachment; filename="{file_name}"'
                    # Find the template and render it.
                    template = get_template(
                        "reports/most_requested_parts_result_pdf.html"
                    )
                    html = template.render(context)

                    # Create PDF and return.
                    pisa_status = pisa.CreatePDF(
                        html, dest=response, link_callback=link_callback
                    )
                    # pisa_status = pisa.CreatePDF(html, dest=response)
                    if not pisa_status.err:
                        return response
                    else:
                        return HttpResponse(
                            f"An error ocurred while generating the report. Please try again, or contact the system administrator. Error: <pre>{html}<pre>"
                        )

                messages.success(request, "Report generated successfully.")
            except Exception as e:
                messages.error(
                    request,
                    f"An error ocurred while generating the report. Please try again, or contact the system administrator. Error: {e}",
                )

        context["form"] = form

        return render(request, "admin/reports_most_requested_parts.html", context)
