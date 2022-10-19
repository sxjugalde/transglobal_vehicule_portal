def compare_entity_field(entity_1, entity_2, field, field_str=""):
    """Compares a property of two entities, returning the difference in a list, when the second entity has non-empty contents that differ with the first."""
    difference = []
    field_str = field_str if field_str else field
    entity_1_field = getattr(entity_1, field, None)
    entity_2_field = getattr(entity_2, field, None)
    if entity_2_field and (entity_1_field != entity_2_field):
        difference.append(f"{field_str}(prev:{entity_1_field}, new:{entity_2_field})")

    return difference
