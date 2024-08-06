def generate_search_query(column_name, value):
    return f"FIND('{value}', {{{column_name}}})" if value else ""
