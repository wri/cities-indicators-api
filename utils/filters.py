def generate_search_query(column_name, value):
    return f"SEARCH(',{value},', ',' & ARRAYJOIN({{{column_name}}}, ',') & ',')"
