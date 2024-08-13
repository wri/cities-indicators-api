from typing import Union, List


def generate_search_query(column_name: str, value: Union[str, List[str]]) -> str:
    """
    Generates a SEARCH query to filter string values from Multiple Select fields in Airtable.

    Args:
        column_name (str): The name of the column to search within.
        value (Union[str, List[str]]): The value or list of values to search for within the specified column.

    Returns:
        str: A string representing the search query for Airtable. If the value is empty,
             an empty string is returned.

    Examples:
        >>> generate_search_query("projects", "data4coolcities")
        "SEARCH('data4coolcities', {projects})"

        >>> generate_search_query("theme", ["Biodiversity", "Climate Change"])
        "AND(SEARCH('Biodiversity', {theme}), SEARCH('Climate Change', {theme}))"

        >>> generate_search_query("theme", "")
        ""
    """
    if isinstance(value, list):
        search_clauses = [f"SEARCH('{v}', {{{column_name}}})" for v in value]
        return f"OR({', '.join(search_clauses)})" if search_clauses else ""

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
        filter_clauses.append(generate_search_query(column, value))

    return f"AND({', '.join(filter_clauses)})" if filter_clauses else ""
