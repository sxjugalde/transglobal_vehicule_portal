from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


def compare_entity_field(entity_1, entity_2, field, field_str=""):
    """Compares a property of two entities, returning the difference in a list, when the second entity has non-empty contents that differ with the first."""
    difference = []
    field_str = field_str if field_str else field
    entity_1_field = getattr(entity_1, field, None)
    entity_2_field = getattr(entity_2, field, None)
    if entity_2_field and (entity_1_field != entity_2_field):
        difference.append(f"{field_str}(prev:{entity_1_field}, new:{entity_2_field})")

    return difference


def is_integer(s: str) -> bool:
    # type: (str) -> bool
    """Checks if a string value is an integer."""
    try:
        int(s)
        return True
    except ValueError:
        return False


def save_entity_iterable_to_db(entity_iterable):
    """Processes the received iterable of entities to the database."""
    if isinstance(entity_iterable, dict):
        for index, entity in entity_iterable.items():
            entity.save()
    elif isinstance(entity_iterable, list):
        for entity in entity_iterable:
            entity.save()
    else:
        raise Exception("Invalid parameter received. Not a list or dictionary.")


def check_staff_permission(user, permission: str):
    """Check if user is logged, is staff and has corresponding permissions"""
    if user and user.is_staff and user.has_perm(permission):
        return
    else:
        raise PermissionDenied()
