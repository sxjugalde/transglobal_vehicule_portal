from django import template

register = template.Library()


@register.inclusion_tag("partials/bom_structure_treeview_row.html")
def bom_structure_treeview_row(
    container: dict,  # Container is the assembly/subassembly, and contains purchase_assemblies and parts dictionaries.
    bom_id: int,
    row_actions: list = None,
    is_admin: bool = False,
):
    """Creates the HTML treeview structure to be used in the template for each BOMRow."""

    return {
        "container": container,
        "bom_id": bom_id,
        "row_actions": row_actions,
        "is_admin": is_admin,
    }
