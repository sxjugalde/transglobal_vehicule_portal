from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum

from vehicles.models.BOMRow import BOMRow
from vehicles.models.Vehicle import Vehicle
from vehicles.logic.BOMRowLogic import get_bom_row_purchase_assembly_code
from ..models.Order import Order
from ..models.Cart import Cart
from ..models.CartRow import CartRow
from .EmailLogic import send_quote_request_submitted_email

USER_MODEL = get_user_model()


def get_cart_details(cart: Cart) -> dict:
    """Obtains the cart's details from the DB and returns these details separated by vehicle as a dict."""

    # Fetch only required information for detailed structure
    rows = cart.rows.order_by(
        "vehicle_identification_number",
        "purchase_assembly_full_code",
        "part_full_code",
        "assembly_code",
        "subassembly_full_code",
    ).all()
    structure = {}

    for row in rows:
        # Build part/PA structure.
        if row.vehicle_identification_number not in structure:
            structure[row.vehicle_identification_number] = {
                "nickname": row.vehicle_nickname,
                "bom_name": row.bom_name,
                "bom_code": row.bom_code,
                "purchase_assemblies": {},
                "parts": {},
            }

        part_detail_dict = {
            "part_full_code": row.part_full_code,
            "part_name": row.part_name,
            "part_uses": row.part_uses,
            "part_location": row.subassembly_full_code
            if row.subassembly_full_code
            else row.assembly_code,
            "quantity": row.quantity,
        }

        if row.purchase_assembly_full_code:  # It's a PA.
            if (
                row.purchase_assembly_full_code
                not in structure[row.vehicle_identification_number][
                    "purchase_assemblies"
                ]
            ):
                # Initialize.
                structure[row.vehicle_identification_number]["purchase_assemblies"][
                    row.purchase_assembly_full_code
                ] = {
                    "quantity": row.quantity,
                    "contents": [],
                }  # Set quantity here, since it should be the same in all rows.
            structure[row.vehicle_identification_number]["purchase_assemblies"][
                row.purchase_assembly_full_code
            ]["contents"].append(part_detail_dict)
        else:  # It's a part.
            if (
                row.part_full_code
                not in structure[row.vehicle_identification_number]["parts"]
            ):
                # Initialize.
                structure[row.vehicle_identification_number]["parts"][
                    row.part_full_code
                ] = []
            structure[row.vehicle_identification_number]["parts"][
                row.part_full_code
            ].append(part_detail_dict)

    return structure


def upsert_or_delete_cart_rows(
    user: USER_MODEL,
    vehicle_id: str,
    bom_row_id: str,
    quantity: str = "0",
) -> list:
    """
    Updates (or creates if it doesn't exist) a row inside a user's cart.
    Deletes it if quantity is 0. Creates the active cart if it doesn't exist.
    Returns BOMRow ids that were added/updated/deleted in cart.
    """
    with transaction.atomic():
        quantity = int(quantity)

        # Fetch user's active cart or create new one.
        cart = Cart.objects.filter(created_by=user, is_current=True).first()

        if not cart:
            cart = Cart.objects.create(
                is_current=True, created_by=user, modified_by=user
            )

        # Check if row is part of a PA, and fetch other rows if it is.
        pa_code = get_bom_row_purchase_assembly_code(bom_row_id=bom_row_id)

        affected_bom_row_ids = [int(bom_row_id)]
        if pa_code:
            affected_bom_row_ids = list(
                BOMRow.objects.filter(
                    bom__vehicle__id=vehicle_id,
                    purchase_assembly_part__purchase_assembly__full_code=pa_code,
                ).values_list("id", flat=True)
            )

        # Check if cart rows already exists in cart.
        existing_cart_rows = CartRow.objects.filter(
            cart=cart, vehicle_id=vehicle_id, bom_row_id__in=affected_bom_row_ids
        ).all()

        # Create/update/delete rows.
        if quantity > 0:
            existing_cart_rows_dict = {
                cart_row.bom_row_id: cart_row for cart_row in existing_cart_rows
            }
            new_cart_rows = []
            for row_id in affected_bom_row_ids:
                if row_id not in existing_cart_rows_dict:
                    new_cart_rows.append(
                        CartRow(
                            cart=cart,
                            vehicle_id=vehicle_id,
                            bom_row_id=row_id,
                            quantity=quantity,
                            created_by=user,
                            modified_by=user,
                        )
                    )
                else:
                    cart_row = existing_cart_rows_dict[row_id]
                    cart_row.quantity = quantity
                    cart_row.modified_by = user

            # Mass insert.
            if new_cart_rows:
                # Set historical values manually, because bulk_create doesn't call save()
                new_cart_rows = set_cart_rows_historical_values(
                    cart_row_list=new_cart_rows, vehicle_id=vehicle_id
                )
                CartRow.objects.bulk_create(new_cart_rows)

            # Mass update.
            if existing_cart_rows:
                CartRow.objects.bulk_update(
                    existing_cart_rows, ["quantity", "modified_by"]
                )
        else:
            # Mass delete.
            existing_cart_rows.delete()

        return affected_bom_row_ids


def set_cart_rows_historical_values(cart_row_list: list, vehicle_id: int) -> list:
    """Set's auxiliary historical values for each cart_row inside cart_row_list."""
    # Fetch auxiliary information for every cart_row.
    vehicle = Vehicle.objects.select_related("bom").get(id=vehicle_id)

    bom_rows_ids = [cart_row.bom_row_id for cart_row in cart_row_list]
    bom_rows_values = BOMRow.objects.filter(id__in=bom_rows_ids).values(
        "id",
        "quantity",
        "assembly__code",
        "assembly__name",
        "subassembly__full_code",
        "subassembly__name",
        "part__full_code",
        "part__name",
        "purchase_assembly_part__purchase_assembly__full_code",
        "purchase_assembly_part__quantity",
        "purchase_assembly_part__part__full_code",
        "purchase_assembly_part__part__name",
    )
    bom_rows_values = {bom_row["id"]: bom_row for bom_row in bom_rows_values}

    # Set values
    for cart_row in cart_row_list:
        cart_row.vehicle_identification_number = vehicle.identification_number or ""
        cart_row.vehicle_nickname = vehicle.nickname or ""
        cart_row.bom_name = vehicle.bom.name or ""
        cart_row.bom_code = vehicle.bom.code or ""
        cart_row.bom_revision = vehicle.bom.revision or ""

        cart_row.assembly_code = (
            bom_rows_values[cart_row.bom_row_id]["assembly__code"] or ""
        )
        cart_row.assembly_name = (
            bom_rows_values[cart_row.bom_row_id]["assembly__name"] or ""
        )
        cart_row.subassembly_full_code = (
            bom_rows_values[cart_row.bom_row_id]["subassembly__full_code"] or ""
        )
        cart_row.subassembly_name = (
            bom_rows_values[cart_row.bom_row_id]["subassembly__name"] or ""
        )

        if bom_rows_values[cart_row.bom_row_id]["part__full_code"]:
            # It's a part.
            cart_row.part_full_code = (
                bom_rows_values[cart_row.bom_row_id]["part__full_code"] or ""
            )
            cart_row.part_name = (
                bom_rows_values[cart_row.bom_row_id]["part__name"] or ""
            )
            cart_row.part_uses = bom_rows_values[cart_row.bom_row_id]["quantity"] or ""
        elif bom_rows_values[cart_row.bom_row_id][
            "purchase_assembly_part__purchase_assembly__full_code"
        ]:
            # It's a PA.
            cart_row.purchase_assembly_full_code = (
                bom_rows_values[cart_row.bom_row_id][
                    "purchase_assembly_part__purchase_assembly__full_code"
                ]
                or ""
            )
            cart_row.part_full_code = (
                bom_rows_values[cart_row.bom_row_id][
                    "purchase_assembly_part__part__full_code"
                ]
                or ""
            )
            cart_row.part_name = (
                bom_rows_values[cart_row.bom_row_id][
                    "purchase_assembly_part__part__name"
                ]
                or ""
            )
            cart_row.part_uses = (
                bom_rows_values[cart_row.bom_row_id]["purchase_assembly_part__quantity"]
                or ""
            )

    return cart_row_list


def submit_cart(cart: Cart, request):
    """Submit's the cart as an order."""
    with transaction.atomic():
        # Set cart as submitted.
        user = request.user
        cart.is_current = False
        cart.modified_by = user
        cart.save()

        # Create new order.
        order = Order.objects.create(
            cart=cart,
            company=user.company,
            user_username=user.username,
            user_email=user.email,
            company_name=user.company.name,
            created_by=user,
            modified_by=user,
        )

        send_quote_request_submitted_email(request, order)


def get_most_requested_items(from_date, to_date, count=10, bom_id=None) -> dict:
    """Fetches information on the most requested parts/PAs in the system."""
    filtered_orders_cart_ids = Order.objects.filter(
        created_on__gte=from_date, created_on__lte=to_date
    ).values_list("cart_id", flat=True)

    # Obtain filtered information for orders in the DB.
    # Initial filters setup.
    filtered_grouped_parts = CartRow.objects.filter(
        cart_id__in=filtered_orders_cart_ids
    ).filter(purchase_assembly_full_code=u"")

    filtered_grouped_purchase_assemblies = CartRow.objects.filter(
        cart_id__in=filtered_orders_cart_ids
    ).exclude(purchase_assembly_full_code=u"")

    # Filter by BOM, if required.
    if bom_id:
        filtered_grouped_parts = filtered_grouped_parts.filter(bom_row__bom_id=bom_id)

        filtered_grouped_purchase_assemblies = (
            filtered_grouped_purchase_assemblies.filter(bom_row__bom_id=bom_id)
        )

    # Grouped parts.
    filtered_grouped_parts = (
        filtered_grouped_parts.values(
            "part_full_code", "part_name"
        )  # Group by part full code.
        .annotate(quantity_sum=Sum("quantity"))  # SUM quantities.
        .order_by("-quantity_sum")
        .all()[:count]
    )

    # PAs summarized and separated by vehicle and cart.
    filtered_grouped_purchase_assemblies = filtered_grouped_purchase_assemblies.values(
        "purchase_assembly_full_code",
        "cart_id",
        "vehicle_id",
    ).annotate(  # Group by PA full code, cart ID and vehicle ID.
        quantity_sum=Sum("quantity", distinct=True)
    )  # SUM quantities.

    # Group PA's again, now by code. SUM quantity_sum again.
    summarized_purchase_assemblies = {}
    for row in filtered_grouped_purchase_assemblies:
        if row["purchase_assembly_full_code"] not in summarized_purchase_assemblies:
            summarized_purchase_assemblies[row["purchase_assembly_full_code"]] = {
                "purchase_assembly_full_code": row["purchase_assembly_full_code"],
                "quantity_sum": row["quantity_sum"],
            }
        else:
            summarized_purchase_assemblies[row["purchase_assembly_full_code"]][
                "quantity_sum"
            ] += row["quantity_sum"]

    # Transform to list. Sort and limit PAs, manually.
    summarized_purchase_assemblies = list(summarized_purchase_assemblies.values())
    summarized_purchase_assemblies = sorted(
        summarized_purchase_assemblies, key=lambda x: x["quantity_sum"], reverse=True
    )[:count]

    return {
        "parts": list(filtered_grouped_parts),
        "purchase_assemblies": summarized_purchase_assemblies,
    }
