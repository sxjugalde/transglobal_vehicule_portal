from django import template

register = template.Library()

# Example:
# cart_details: {'123456789': {'nickname': 'Vehicle 1', 'purchase_assemblies': {'A1000202': {'quantity': 2, 'contents': [{'part_full_code': '200771A', 'part_name': 'Weldment: Fork Pin', 'part_uses': '2', 'part_location': '1010S01', 'quantity': 2}, {'part_full_code': '200772A', 'part_name': 'Weldment: Fork Pin - Stop Block', 'part_uses': '2', 'part_location': '1010S02', 'quantity': 2}]}}, 'parts': {'20078': [{'part_full_code': '20078', 'part_name': 'Fork Main', 'part_uses': '3', 'part_location': '1020', 'quantity': 6}]}}, '987654321': {'nickname': 'Vehicle 2', 'purchase_assemblies': {}, 'parts': {'20078': [{'part_full_code': '20078', 'part_name': 'Fork Main', 'part_uses': '3', 'part_location': '1020', 'quantity': 3}]}}}
# header_classes: ['module']


@register.inclusion_tag("partials/cart_details.html")
def cart_details(
    cart_details: dict,
    header_classes: list = [],
    row_classes: list = [],
    is_admin: bool = False,
):
    """Creates the HTML for the order details."""

    return {
        "cart_details": cart_details,
        "header_classes": header_classes,
        "row_classes": row_classes,
        "is_admin": is_admin,
    }
