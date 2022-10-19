def save_entity_iterable_to_db(entity_iterable):
    """Processes the received iterable of entities to the database."""
    if isinstance(entity_iterable, dict):
        for index, entity in entity_iterable.items():
            entity.save()
    elif isinstance(entity_iterable, list):
        for entity in entity_iterable:
            entity.save()
    else:
        raise Exception("Invalid parameter received. Not a list or dictionary.")
