from ..models.Part import Part


def get_part_verbose_str(
    part_full_code: str,
    part_name: str,
    quantity: int = 1,
) -> str:
    """Returns a more readable version of the entity's str representation, without an instance."""
    return "[{}] [{}] {}".format(
        "P" + part_full_code,
        "Uses " + str(quantity),
        part_name,
    )


def get_all_parts():
    return Part.objects.order_by("full_code").all()
