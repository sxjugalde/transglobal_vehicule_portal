from django import template

register = template.Library()


@register.inclusion_tag("partials/bom_structure_treeview.html")
def bom_structure_treeview(
    bom_id: int, bom_structure: dict, row_actions: list = None, is_admin: bool = False
):
    """Creates the HTML treeview structure (ul/li) to be used in the template."""

    return {
        "bom_id": bom_id,
        "bom_structure": bom_structure,
        "row_actions": row_actions,
        "is_admin": is_admin,
    }
