from django.contrib.auth.models import Group


def auto_assign_groups(
    user, staff_group_name: str = "Staff", customer_group_name: str = "Customer"
):
    """Automatically assigns the Staff or Customer group to a new user, when the requesting use is a staff member without superuser rights."""
    groups = user.groups.all()
    belongs_to_staff = groups.filter(name=staff_group_name).exists()
    # belongs_to_customer = groups.filter(name=customer_group_name).exists()
    staff_group = Group.objects.get(name=staff_group_name)
    # customer_group = Group.objects.get(name=customer_group_name)

    if user.is_staff:
        if not belongs_to_staff:
            user.groups.add(staff_group)

        # if belongs_to_customer: # Delete wrong group.
        # self.groups.remove(customer_group)
    elif not user.is_staff:  # Delete wrong group.
        if belongs_to_staff:
            user.groups.remove(staff_group)

        # if not belongs_to_customer: # It's a new customer.
        #     self.groups.add(customer_group)
    user.save()
