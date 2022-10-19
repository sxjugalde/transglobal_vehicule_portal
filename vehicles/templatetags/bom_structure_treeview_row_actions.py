from django import template

register = template.Library()


@register.inclusion_tag("partials/bom_structure_treeview_row_actions.html")
def bom_structure_treeview_row_actions(
    bom_id: int,
    row: dict,
    row_actions: list = None,
    is_admin: bool = False,
):
    """Creates the HTML actions to be used in the template, on each final row of the treeview (PA or part)."""

    return {
        "bom_id": bom_id,
        "row": row,
        "row_actions": row_actions,
        "is_admin": is_admin,
    }
