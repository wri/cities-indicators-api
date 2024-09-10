from typing import Dict, List, Optional
from pydantic import BaseModel


class LayerResponse(BaseModel):
    city_id: str
    file_type: str
    layer_id: str
    layer_path: str
    legend_styling: Optional[List[Dict]]
    map_styling: Optional[List[Dict]]
