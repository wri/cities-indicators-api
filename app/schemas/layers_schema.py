from typing import Dict, List, Optional
from pydantic import BaseModel


class LayerResponse(BaseModel):
    city_id: str
    layer_id: str
    layer_path: str
    file_type: str
    styling: Optional[List[Dict]]
