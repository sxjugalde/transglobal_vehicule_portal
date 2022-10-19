import os
import logging

from django.contrib import admin, messages
from django.contrib.auth import get_user
from django.db import models, transaction
from django import forms
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import get_object_or_404, render, redirect

from ..forms.BOMAdminForm import BOMAdminForm
from ..forms.AddBOMRowSelectionForm import AddBOMRowSelectionForm
from ..forms.AddBOMRowPartForm import AddBOMRowPartForm
from ..forms.AddBOMRowPurchaseAssemblyForm import (
    AddBOMRowPurchaseAssemblyForm,
    SelectPartLocationForm,
)
from ..models.BOM import BOM
from ..models.BOMRow import BOMRow
from ..logic.AssemblyLogic import (
    get_assembly_subassembly_location,
    get_all_assembly_subassembly_locations_by_vehicle_family,
)
from ..logic.BOMRowLogic import save_pa_bom_row, save_part_bom_row
from ..logic.BOMLogic import get_bom_structure
from parts.models.PurchaseAssemblyPart import (
    get_purchase_assembly_part_verbose_str,
    get_all_purchase_assembly_parts,
)
from utils.mixins.AuditableMixin import AuditableMixin
from utils.logic.check_staff_permission import check_staff_permission


@admin.register(BOM)
class BOMAdmin(AuditableMixin, admin.ModelAdmin):
    form = BOMAdminForm
    add_form_template = "admin/vehicles_add_bom.html"
    change_list_template = "admin/vehicles_bom_change_list.html"
    actions = None
    save_as = True
    filter_horizontal = ("files",)
    list_display = (
        "name",
        "code",
        "revision",
        "vehicle_family",
        "modified_on",
        "modified_by",
        "image_tag",
        "actions_html",
    )
    list_select_related = ["vehicle_family", "modified_by"]
    list_filter = ["vehicle_family", "modified_on"]
    search_fields = ["name", "code"]

    formfield_overrides = {
        models.TextField: {
            "widget": forms.Textarea(
                attrs={
                    "rows": 2,
                    "cols": 80,
                }
            )
        },
    }

    def actions_html(self, obj):
        return format_html(
            '<a class="button" href="{bom_structure_url}" title="View structure" aria-label="View structure"><i class="fa fa-eye"></i></a>',
            bom_structure_url=reverse(
                "admin:vehicles_bom_structure",
                args=(obj.id,),
            ),
        )

    actions_html.allow_tags = True
    actions_html.short_description = "Actions"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:bom_id>/structure/",
                self.admin_site.admin_view(self.bom_structure),
                name="vehicles_bom_structure",
            ),
            path(
                "<int:bom_id>/bomrow/<int:bom_row_id>/delete",
                self.admin_site.admin_view(self.delete_bom_row),
                name="vehicles_bomrow_delete",
            ),
            path(
                "<int:bom_id>/bomrow/add",
                self.admin_site.admin_view(self.add_bom_row),
                name="vehicles_bomrow_add",
            ),
        ]
        return custom_urls + urls

    def get_form(self, request, obj=None, **kwargs):
        form = super(BOMAdmin, self).get_form(request, obj, **kwargs)
        form.user = get_user(request)  # Add request user to form.
        form.is_saveasnew = "_saveasnew" in request.POST

        return form

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["vehicle_family", "import_file"]
        else:
            return []

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            # OnCreate: Get import_helper from form and process related entities in a transaction.
            if change is False:
                if "_saveasnew" not in request.POST:
                    super(BOMAdmin, self).save_model(request, obj, form, change)
                    if obj.id is not None:
                        form.import_helper.process_bom_entities_to_db(obj)
                else:
                    # Set import file and duplicate rows
                    original_pk = request.resolver_match.kwargs["object_id"]
                    original_obj = BOM.objects.prefetch_related("rows").get(
                        pk=original_pk
                    )
                    # Set readonly and file/image fields.
                    obj.vehicle_family = original_obj.vehicle_family
                    obj.import_file = original_obj.import_file
                    if not obj.thumbnail.name and original_obj.thumbnail.name:
                        obj.thumbnail = original_obj.thumbnail

                    super(BOMAdmin, self).save_model(request, obj, form, change)

                    if obj.id is not None:
                        self.duplicate_bom_rows(original_obj, obj, request.user)
            else:
                super(BOMAdmin, self).save_model(request, obj, form, change)

    def duplicate_bom_rows(self, original_bom, new_bom, user):
        """Duplicates all the BOM rows that reference an original object, and maps them to a new BOM."""
        for row in original_bom.rows.all():
            row.pk = None
            row.bom = new_bom
            row.created_by = user
            row.modified_by = user
            row.save()

    def bom_structure(self, request, bom_id: int):
        """Returns the BOM edit structure screen."""
        # check_staff_permission(request.user, "vehicles.change_bom")
        bom = get_object_or_404(BOM, pk=bom_id)

        # Setup context and render template
        context = self.admin_site.each_context(request)
        context["opts"] = self.model._meta
        context["title"] = f"{bom} - Structure"
        context["bom"] = bom
        context["bom_structure"] = get_bom_structure(bom)
        context["row_actions"] = ["delete"]
        context["vehicles_bomrow_add_url"] = reverse(
            "admin:vehicles_bomrow_add",
            args=(bom_id,),
        )

        return render(request, "admin/vehicles_bom_structure.html", context)

    def delete_bom_row(self, request, bom_id: int, bom_row_id: int):
        """Returns the BOMRow delete screen if GET, or deletes BOMRows if POST."""
        # check_staff_permission(request.user, "vehicles.delete_bom_row")
        bom = get_object_or_404(BOM, pk=bom_id)
        bom_row = get_object_or_404(BOMRow, pk=bom_row_id)

        # Review BOMRow
        rows_to_delete = bom_row
        if bom_row.purchase_assembly_part:
            rows_to_delete = bom.rows.filter(
                purchase_assembly_part__purchase_assembly=bom_row.purchase_assembly_part.purchase_assembly
            )

        if request.method == "POST":
            # Delete rows and redirect to bom-structure.
            try:
                with transaction.atomic():
                    rows_deleted = rows_to_delete.delete()
                    bom.modified_by = request.user
                    bom.save()
                    messages.success(
                        request,
                        "{deleted_count} BOM row(s) deleted successfully.".format(
                            deleted_count=rows_deleted[0]
                        ),
                    )
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Error: {e}")
                messages.error(
                    request,
                    "There was an error while deleting the BOM row(s), please try again or contact the system administrator.",
                )

            return redirect(
                "admin:vehicles_bom_structure", bom_id=bom_id, permanent=True
            )
        else:
            # Setup context and render template
            context = self.admin_site.each_context(request)
            context["opts"] = self.model._meta
            context["title"] = "Are you sure?"
            context["cancel_url"] = reverse(
                "admin:vehicles_bom_structure",
                args=(bom_id,),
            )
            context["bom"] = bom
            context["is_purchase_assembly"] = bom_row.purchase_assembly_part is not None
            context["part_location"] = get_assembly_subassembly_location(
                assembly_code=bom_row.assembly.code,
                assembly_name=bom_row.assembly.name,
                subassembly_code=bom_row.subassembly.code
                if bom_row.subassembly
                else None,
                subassembly_name=bom_row.subassembly.name
                if bom_row.subassembly
                else None,
            )

            if bom_row.purchase_assembly_part:
                # Fetch and set descriptions for each purchase assembly part row.
                rows_to_delete_values = rows_to_delete.values(
                    "id",
                    "assembly__code",
                    "assembly__name",
                    "subassembly__code",
                    "subassembly__name",
                    "purchase_assembly_part__purchase_assembly__full_code",
                    "purchase_assembly_part__quantity",
                    "purchase_assembly_part__part__full_code",
                    "purchase_assembly_part__part__name",
                )
                purchase_assembly_members = []
                for row in list(rows_to_delete_values):
                    if row["id"] != bom_row.id:
                        row_location = "[{}] {} - [{}] {}".format(
                            row["assembly__code"],
                            row["assembly__name"],
                            row["subassembly__code"],
                            row["subassembly__name"],
                        )
                        purchase_assembly_str = get_purchase_assembly_part_verbose_str(
                            purchase_assembly_full_code=row[
                                "purchase_assembly_part__purchase_assembly__full_code"
                            ],
                            part_full_code=row[
                                "purchase_assembly_part__part__full_code"
                            ],
                            part_name=row["purchase_assembly_part__part__name"],
                            quantity=row["purchase_assembly_part__quantity"],
                        )
                        purchase_assembly_members.append(
                            " - ".join([row_location, purchase_assembly_str])
                        )
                    else:
                        context["part_name"] = "[{}] [{}] {}".format(
                            row["purchase_assembly_part__purchase_assembly__full_code"],
                            row["purchase_assembly_part__part__full_code"],
                            row["purchase_assembly_part__part__name"],
                        )
                context["purchase_assembly_members"] = purchase_assembly_members
            else:
                context["part_name"] = "[{}] {}".format(
                    bom_row.part.full_code, bom_row.part.name
                )

            return render(request, "admin/vehicles_delete_bom_row.html", context)

    def add_bom_row(self, request, bom_id: int):
        """Returns the BOMRow add screen if GET, or adds BOMRows if POST."""
        # check_staff_permission(request.user, "vehicles.add_bom_row")
        bom = get_object_or_404(BOM, pk=bom_id)

        SelectPartLocationFormSet = forms.formset_factory(
            SelectPartLocationForm, extra=0
        )

        # Setup initial context
        context = self.admin_site.each_context(request)
        context["opts"] = self.model._meta
        context["title"] = 'Add part or purchase assembly to BOM "{}"'.format(str(bom))
        context["bom"] = bom

        if request.method == "POST":
            selection_form = AddBOMRowSelectionForm(request.POST, prefix="selection")
            context["selection_form"] = selection_form

            part_form = AddBOMRowPartForm(request.POST, prefix="part")
            part_form.load_part_choices()
            part_form.load_part_locations(vehicle_family_id=bom.vehicle_family_id)
            context["part_form"] = part_form

            purchase_assembly_form = AddBOMRowPurchaseAssemblyForm(
                request.POST, prefix="purchase_assembly"
            )
            purchase_assembly_form.load_purchase_assembly_choices()
            locations = get_all_assembly_subassembly_locations_by_vehicle_family(
                vehicle_family_id=bom.vehicle_family_id
            )
            part_location_formset = SelectPartLocationFormSet(
                request.POST,
                form_kwargs={"part_location_choices": locations},
            )
            context["purchase_assembly_form"] = purchase_assembly_form
            context["select_pa_location_formset"] = part_location_formset

            if selection_form.is_valid():
                if (
                    selection_form.cleaned_data["part_or_pa_selection"] == "part"
                    and part_form.is_valid()
                ):
                    # Add BOM Rows.
                    try:
                        save_part_bom_row(
                            bom=bom,
                            part_id=int(part_form.cleaned_data["part_to_add"]),
                            quantity=int(part_form.cleaned_data["part_quantity"]),
                            location=part_form.cleaned_data["part_location"],
                            user=request.user,
                        )

                        messages.success(request, "Part added successfully.")

                        return redirect(
                            "admin:vehicles_bom_structure",
                            bom_id=bom_id,
                            permanent=True,
                        )
                    except Exception as e:
                        logger = logging.getLogger(__name__)
                        logger.error(f"Error: {e}")
                        messages.error(
                            request,
                            "An error ocurred while adding the part, please try again or contact the system administrator.",
                        )
                elif (
                    selection_form.cleaned_data["part_or_pa_selection"]
                    == "purchase_assembly"
                    and purchase_assembly_form.is_valid()
                    and part_location_formset.is_valid()
                ):
                    pa_pk = purchase_assembly_form.cleaned_data["pa_to_add"]
                    pa_parts = get_all_purchase_assembly_parts(
                        purchase_assembly_id=pa_pk
                    )

                    # Validate that the PA is not being repeated.
                    if BOMRow.objects.filter(
                        bom=bom, purchase_assembly_part__in=pa_parts
                    ).exists():
                        # TODO: Edge case - Currently unable to add/import repeated PAs. If possible, they should either be distributed in the same way and represented through the quantity in the BOMRow, or marked with an identifier. Show in screen.
                        messages.error(
                            request,
                            "The purchase assembly you've selected is already present in the BOM, and it cannot be repeated. Please select another one.",
                        )
                    else:
                        # Iterate and validate that the count and IDs are correct.
                        pa_part_ids = []
                        part_count = 0
                        for pa_part in pa_parts:
                            part_count += 1
                            pa_part_ids.append(pa_part.id)

                        form_count = 0
                        error_found = False
                        for form in part_location_formset:
                            form_count += 1
                            if form.cleaned_data["pa_part_id"] not in pa_part_ids:
                                error_found = True

                        if part_count != form_count:
                            error_found = True

                        if not error_found:
                            # Add BOM Rows.
                            try:
                                save_pa_bom_row(
                                    pa_id=int(pa_pk),
                                    bom=bom,
                                    locations_form_cleaned_data=part_location_formset.cleaned_data,
                                    user=request.user,
                                )

                                messages.success(
                                    request, "Purchase assembly added successfully."
                                )

                                return redirect(
                                    "admin:vehicles_bom_structure",
                                    bom_id=bom_id,
                                    permanent=True,
                                )
                            except Exception as e:
                                logger = logging.getLogger(__name__)
                                logger.error(f"Error: {e}")
                                messages.error(
                                    request,
                                    "An error ocurred while adding the PA, please try again or contact the system administrator.",
                                )
                        else:
                            messages.error(
                                request,
                                "An incorrect number or selection of parts were sent for the specified PA. Please correct the form and try again.",
                            )
                else:
                    messages.error(
                        request,
                        "There were errors in your form, please correct them and try again.",
                    )

            # return redirect("admin:vehicles_bomrow_add", bom_id=bom_id, permanent=True)
        else:
            # Setup forms
            selection_form = AddBOMRowSelectionForm(
                prefix="selection", initial={"part_or_pa_selection": "part"}
            )
            context["selection_form"] = selection_form

            part_form = AddBOMRowPartForm(prefix="part")
            part_form.load_part_choices()
            part_form.load_part_locations(vehicle_family_id=bom.vehicle_family_id)
            context["part_form"] = part_form

            purchase_assembly_form = AddBOMRowPurchaseAssemblyForm(
                prefix="purchase_assembly"
            )
            purchase_assembly_form.load_purchase_assembly_choices()
            part_location_formset = SelectPartLocationFormSet(
                form_kwargs={
                    "part_location_choices": part_form.fields["part_location"].choices
                },
            )
            context["purchase_assembly_form"] = purchase_assembly_form
            context["select_pa_location_formset"] = part_location_formset

        return render(request, "admin/vehicles_add_bom_row.html", context)
