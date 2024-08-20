from typing import Optional
from app.const import indicators_table


def fetch_indicators(filter_formula: Optional[str] = None):
    return indicators_table.all(view="api", formula=filter_formula)


def fetch_first_indicator(filter_formula: Optional[str] = None):
    return indicators_table.first(view="api", formula=filter_formula)
