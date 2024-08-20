from typing import Optional
from app.const import cities_table


def fetch_cities(filter_formula: Optional[str] = None):
    return cities_table.all(view="api", formula=filter_formula)
