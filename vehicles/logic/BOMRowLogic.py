from django.db import transaction

from ..models.BOM import BOM
from ..models.BOMRow import BOMRow
from ..models.Assembly import Assembly
from ..models.Subassembly import Subassembly
from parts.models.PurchaseAssemblyPart import PurchaseAssemblyPart
from parts.models.Part import Part


def save_pa_bom_row(pa_id: int, bom, locations_form_cleaned_data, user):
    """Saves a BOMRow for a purchase assembly, as received from the AddBOMRowPurchaseAssemblyForm."""
    with transaction.atomic():
        # Aux variables
        rows_to_add = []
        assembly_codes = []
        subassembly_codes = []
        pa_part_ids = []

        assemblies = []
        subassemblies = []
        pa_parts = []

        # Fetch data.
        for data in locations_form_cleaned_data:
            location_list = data["part_location"].split("-")
            assembly_codes.append(location_list[0])
            if len(location_list) > 1:
                subassembly_codes.append(location_list[0] + location_list[1])
            pa_part_ids.append(int(data["pa_part_id"]))

        assemblies = Assembly.objects.filter(
            vehicle_family=bom.vehicle_family, code__in=assembly_codes
        ).all()
        subassemblies = Subassembly.objects.filter(
            vehicle_family=bom.vehicle_family, full_code__in=subassembly_codes
        ).all()
        pa_parts = PurchaseAssemblyPart.objects.filter(pk__in=pa_part_ids).all()

        # Build rows and create them.
        for data in locations_form_cleaned_data:
            location_list = data["part_location"].split("-")
            assembly = assemblies.filter(code=location_list[0]).get()
            subassembly = (
                subassemblies.filter(
                    full_code=location_list[0] + location_list[1]
                ).get()
                if len(location_list) > 1
                else None
            )
            pa_part = pa_parts.get(pk=int(data["pa_part_id"]))
            row = BOMRow(
                bom=bom,
                assembly=assembly,
                subassembly=subassembly,
                purchase_assembly_part=pa_part,
                part=None,
                quantity=1,  # 1 for now.
                created_by=user,
                modified_by=user,
            )
            row.save()


def save_part_bom_row(bom: BOM, part_id: int, quantity: int, location: str, user):
    """Saves a BOMRow for a part, as received from the AddBOMRowPartForm."""
    location_list = location.split("-")
    assembly = Assembly.objects.filter(
        vehicle_family=bom.vehicle_family, code=location_list[0]
    ).get()
    subassembly = (
        Subassembly.objects.filter(
            vehicle_family=bom.vehicle_family,
            full_code=location_list[0] + location_list[1],
        ).get()
        if len(location_list) > 1
        else None
    )
    part = Part.objects.get(pk=part_id)
    row = BOMRow(
        bom=bom,
        assembly=assembly,
        subassembly=subassembly,
        purchase_assembly_part=None,
        part=part,
        quantity=quantity,
        created_by=user,
        modified_by=user,
    )
    row.save()


def get_bom_row_purchase_assembly_code(bom_row_id: int) -> str:
    """Check if the BOMRow is a PA member, and returns the PA code."""
    bom_row = BOMRow.objects.select_related(
        "purchase_assembly_part__purchase_assembly"
    ).get(pk=bom_row_id)

    if not bom_row.purchase_assembly_part:
        return None
    else:
        return bom_row.purchase_assembly_part.purchase_assembly.full_code
