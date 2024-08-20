from typing import Optional
from app.const import datasets_table


def fetch_datasets(filter_formula: Optional[str] = None):
    return datasets_table.all(view="api", formula=filter_formula)
