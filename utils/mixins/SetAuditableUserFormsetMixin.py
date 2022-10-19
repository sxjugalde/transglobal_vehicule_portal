from ..forms.SetAuditableUserInlineFormset import SetAuditableUserInlineFormset


class SetAuditableUserFormsetMixin(object):
    """Use a generic formset which populates the 'created_by' and 'modified_by' model fields with the currently logged in user."""

    formset = SetAuditableUserInlineFormset

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(SetAuditableUserFormsetMixin, self).get_formset(
            request, obj, **kwargs
        )
        formset.request = request
        return formset
