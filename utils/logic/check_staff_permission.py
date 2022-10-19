from django.core.exceptions import PermissionDenied


def check_staff_permission(user, permission: str):
    """Check if user is logged, is staff and has corresponding permissions"""
    if user and user.is_staff and user.has_perm(permission):
        return
    else:
        raise PermissionDenied()
