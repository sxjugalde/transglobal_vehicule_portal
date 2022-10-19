from ..models.Assembly import Assembly
from ..models.Subassembly import Subassembly


def get_all_assembly_subassembly_locations_by_vehicle_family(
    vehicle_family_id: int,
) -> list:
    """Returns a list with every possible location belonging to a specific vehicle family. Key = - separated identifiers, Value = Readable location."""
    assemblies = (
        Assembly.objects.filter(vehicle_family_id=vehicle_family_id)
        .order_by("code")
        .prefetch_related("subassemblies")
        .all()
    )
    locations = []

    for assembly in assemblies:
        locations.append(
            (
                assembly.code,
                get_assembly_subassembly_location(
                    assembly_code=assembly.code,
                    assembly_name=assembly.name,
                ),
            )
        )
        for subassembly in assembly.subassemblies.order_by("code").all():
            locations.append(
                (
                    "{}-{}".format(assembly.code, subassembly.code),
                    get_assembly_subassembly_location(
                        assembly_code=assembly.code,
                        assembly_name=assembly.name,
                        subassembly_code=subassembly.code,
                        subassembly_name=subassembly.name,
                    ),
                )
            )

    return locations


def get_assembly_subassembly_location(
    assembly_code: str,
    assembly_name: str,
    subassembly_code: str = None,
    subassembly_name: str = None,
) -> str:
    """Returns a str with a structured location."""
    location = "[{}] {}".format(assembly_code, assembly_name)

    if subassembly_code and subassembly_name:
        location = " - ".join(
            [location, "[{}] {}".format(subassembly_code, subassembly_name)]
        )

    return location
