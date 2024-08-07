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


def construct_filter_formula(filters: dict) -> str:
    """
    Constructs the Airtable filter formula based on provided filter parameters.

    Args:
        filters (dict): A dictionary where the key is the column name and the value is the filter value.

    Returns:
        str: A string representing the filter formula for Airtable.
    """
    filter_clauses = []
    for column, value in filters.items():
        if column.endswith("_in"):
            actual_column = column[:-3]  # Remove '_in' to get the actual column name
            filter_clauses.append(generate_search_query(actual_column, value))
        else:
            filter_clauses.append(f"{{{column}}} = '{value}'")
    
    return f"AND({', '.join(filter_clauses)})" if filter_clauses else ""
