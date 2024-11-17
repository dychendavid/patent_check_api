from sqlalchemy import inspect

def get_model_fields(model_class, exclude: list = None, include: list = None):
    """
    Get filtered model fields using inspect
    
    Args:
        model_class: The SQLAlchemy model class
        exclude: List of field names to exclude
        include: List of field names to include (if specified, only these fields will be returned)
    
    Returns:
        list: Filtered field names
    """
    all_fields = [column.name for column in inspect(model_class).columns]

    exclude = exclude or []
    
    if include:
        return [field for field in include if field in all_fields and field not in exclude]
    
    return [field for field in all_fields if field not in exclude]

