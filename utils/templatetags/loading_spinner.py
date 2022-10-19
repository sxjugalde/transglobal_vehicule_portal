from django import template

register = template.Library()


@register.inclusion_tag("partials/loading_spinner.html")
def loading_spinner(text_to_show: str = "Loading..."):
    """Creates the HTML for a loading spinner."""

    return {
        "text_to_show": text_to_show,
    }
