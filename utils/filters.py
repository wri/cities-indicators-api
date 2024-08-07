def generate_find_query(column_name: str, value: str) -> str:
    """
    Generates a case-sensitive FIND query to filter string values from multiple select fields in Airtable.

    Args:
        column_name (str): The name of the column to search within.
        value (str): The value to search for within the specified column.

    Returns:
        str: A string representing the find query for Airtable. If the value is empty, 
             an empty string is returned.
             
    Examples:
        >>> generate_find_query("project", "data4coolcities")
        "FIND('data4coolcities', {project})"
        
        >>> generate_find_query("theme", "Biodiversity")
        "FIND('Biodiversity', {theme})"
        
        >>> generate_find_query("theme", "")
        ""
    """
    return f"FIND('{value}', {{{column_name}}})" if value else ""
