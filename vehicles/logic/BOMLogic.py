from django.contrib.auth import get_user_model

from ..models.BOM import BOM
from ..models.Assembly import get_assembly_str
from ..models.Subassembly import get_subassembly_str
from orders.models.CartRow import CartRow

USER_MODEL = get_user_model()


def get_bom_structure(
    bom: BOM, user: USER_MODEL = None, vehicle_identification_number: str = None
) -> dict:
    """Obtains the entire BOM structure from the DB and returns the hierarchy as a dict."""
    # Fetch only required information for structure
    rows = bom.rows.order_by("assembly__code", "subassembly__code").values(
        "id",
        "quantity",
        "assembly__code",
        "assembly__name",
        "subassembly__code",
        "subassembly__name",
        "part__full_code",
        "part__name",
        "purchase_assembly_part__purchase_assembly__full_code",
        "purchase_assembly_part__quantity",
        "purchase_assembly_part__part__full_code",
        "purchase_assembly_part__part__name",
    )
    structure = {}

    # CustomerPortal: Fetch user's active cart rows which have values related to these BOM rows, in order to show them
    cart_values = {}
    if user and vehicle_identification_number:
        cart_values_list = list(
            CartRow.objects.filter(
                vehicle_identification_number=vehicle_identification_number,
                cart__is_current=True,
                cart__created_by=user,
                bom_row_id__in=[row["id"] for row in rows],
                quantity__gt=0,
            ).values("bom_row_id", "quantity")
        )
        cart_values = {
            cart_value["bom_row_id"]: cart_value["quantity"]
            for cart_value in cart_values_list
        }

    for row in rows:
        # Build assembly/subassembly representation
        assembly_code = row["assembly__code"]
        subassembly_code = row["subassembly__code"]

        # Initialize dicts and setup structure
        if assembly_code and assembly_code not in structure:
            assembly_str = get_assembly_str(
                code=row["assembly__code"], name=row["assembly__name"]
            )
            structure[assembly_code] = {
                "str": assembly_str,
                "subassemblies": {},
                "purchase_assemblies": {},
                "parts": [],
            }
        if (
            subassembly_code
            and subassembly_code not in structure[assembly_code]["subassemblies"]
        ):
            subassembly_str = get_subassembly_str(
                code=row["subassembly__code"], name=row["subassembly__name"]
            )
            structure[assembly_code]["subassemblies"][subassembly_code] = {
                "str": subassembly_str,
                "purchase_assemblies": {},
                "parts": [],
            }

        # Select auxiliary structure depending on if it's inside the assembly or subassembly, and if it's a part or PA.
        part_or_pa = (
            "purchase_assemblies"
            if row["purchase_assembly_part__purchase_assembly__full_code"]
            else "parts"
        )
        structure_aux = (
            structure[assembly_code]["subassemblies"][subassembly_code][part_or_pa]
            if subassembly_code
            else structure[assembly_code][part_or_pa]
        )

        # Check if row has a value in user's cart
        amount_in_cart = 0
        if cart_values and row["id"] in cart_values:
            amount_in_cart = cart_values[row["id"]]

        # Add part/PAP to structure
        if row["part__full_code"]:
            structure_aux.append(
                {
                    "bom_row_id": row["id"],
                    "part_full_code": row["part__full_code"],
                    "part_name": row["part__name"],
                    "part_uses": row["quantity"],
                    "amount_in_cart": amount_in_cart,
                }
            )
        elif row["purchase_assembly_part__purchase_assembly__full_code"]:
            if (
                row["purchase_assembly_part__purchase_assembly__full_code"]
                not in structure_aux
            ):
                structure_aux[
                    row["purchase_assembly_part__purchase_assembly__full_code"]
                ] = []

            structure_aux[
                row["purchase_assembly_part__purchase_assembly__full_code"]
            ].append(
                {
                    "bom_row_id": row["id"],
                    "purchase_assembly_full_code": row[
                        "purchase_assembly_part__purchase_assembly__full_code"
                    ],
                    "part_full_code": row["purchase_assembly_part__part__full_code"],
                    "part_name": row["purchase_assembly_part__part__name"],
                    "part_uses": row["purchase_assembly_part__quantity"],
                    "amount_in_cart": amount_in_cart,
                }
            )
        else:
            raise Exception(
                "There is an error with the BOM's structure. Please contact the system administrator."
            )

    return structure


def get_all_boms():
    return BOM.objects.order_by("code").all()
