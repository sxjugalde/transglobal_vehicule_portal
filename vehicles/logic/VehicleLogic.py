from django.db.models import Q

from ..models.Vehicle import Vehicle


def get_all_company_vehicles_by_location(company_id: int) -> list:
    """Returns a dictionary of locations, with a list of vehicles inside."""
    vehicles = (
        Vehicle.objects.filter(location__company_id=company_id)
        .order_by("location")
        .select_related("location")
        .select_related("bom")
        .select_related("bom__vehicle_family")
        .all()
    )
    locations = {}

    for vehicle in vehicles:
        if vehicle.location.name not in locations:
            locations[vehicle.location.name] = []

        locations[vehicle.location.name].append(vehicle)

    return locations


def search_company_vehicles(company_id: int, search_text: str) -> list:
    """Returns the vehicles from the user's company that match by VIN or nickname."""
    vehicles = (
        Vehicle.objects.filter(location__company_id=company_id)
        .filter(
            Q(identification_number__icontains=search_text)
            | Q(nickname__icontains=search_text)
        )
        .order_by("identification_number")
        .all()
    )

    return vehicles
