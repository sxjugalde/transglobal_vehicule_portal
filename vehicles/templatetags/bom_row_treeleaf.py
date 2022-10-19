from django import template

register = template.Library()


@register.inclusion_tag("partials/bom_row_treeleaf.html")
def bom_row_treeleaf(
    bom_id: int,
    row_id: int,
    row: dict,
    row_actions: list = None,
    is_admin: bool = False,
):
    """Creates the HTML treeview structure (li/actions) to be used in the template."""

    return {
        "bom_id": bom_id,
        "row_id": row_id,
        "row": row,
        "row_actions": row_actions,
        "is_admin": is_admin,
    }
