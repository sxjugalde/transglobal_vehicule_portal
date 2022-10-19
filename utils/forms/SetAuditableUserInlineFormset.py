from django.forms.models import BaseInlineFormSet


class SetAuditableUserInlineFormset(BaseInlineFormSet):
    """This assume you're setting the 'Auditable' model, or that the model has created_by and modified_by fields."""

    def save_new(self, form, commit=True):
        """
        This is called when a new instance is being created.
        """
        obj = super(SetAuditableUserInlineFormset, self).save_new(form, commit=False)

        obj.created_by = self.request.user
        obj.modified_by = self.request.user
        if commit:
            obj.save()
        return obj

    def save_existing(self, form, instance, commit=True):
        """
        This is called when updating an instance.
        """
        obj = super(SetAuditableUserInlineFormset, self).save_existing(
            form, instance, commit=False
        )
        obj.modified_by = self.request.user
        if commit:
            obj.save()
        return obj
