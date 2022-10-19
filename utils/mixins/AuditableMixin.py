class AuditableMixin(
    object,
):
    """A mixin used to set created_by and modified_by fields to current request user."""

    def form_valid(
        self,
        form,
    ):
        if not form.instance.created_by_id:
            form.instance.created_by = self.request.user
        form.instance.modified_by = self.request.user
        return super(AuditableMixin, self).form_valid(form)

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        obj.modified_by = request.user
        return super(AuditableMixin, self).save_model(request, obj, form, change)
