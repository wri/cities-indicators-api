from typing import Dict, List, Optional
from pydantic import BaseModel


class LayerResponse(BaseModel):
    city_id: str
    file_type: str
    layer_id: str
    layer_url: str
    file_type: str
    styling: Optional[List[Dict]]
