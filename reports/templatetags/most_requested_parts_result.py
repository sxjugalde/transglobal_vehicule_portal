from django import template

register = template.Library()


@register.inclusion_tag("reports/most_requested_parts_result.html")
def most_requested_parts_result(report_items: dict, print_pdf: bool = False):
    """Creates the HTML table structure to be used in the template. report_items contains parts and purchase_assemblies."""

    return {
        "report_items": report_items,
        "print_pdf": print_pdf,
    }
