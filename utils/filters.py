def generate_search_query(column_name: str, value: str) -> str:
    """
    Generates a SEARCH query to filter string values from Multiple Select fields in Airtable.

    Args:
        column_name (str): The name of the column to search within.
        value (str): The value to search for within the specified column.

    Returns:
        str: A string representing the search query for Airtable. If the value is empty,
             an empty string is returned.

    Examples:
        >>> generate_search_query("project", "data4coolcities")
        "SEARCH('data4coolcities', {project})"

        >>> generate_search_query("theme", "Biodiversity")
        "SEARCH('Biodiversity', {theme})"

        >>> generate_search_query("theme", "")
        ""
    """
    return f"SEARCH('{value}', {{{column_name}}})" if value else ""
