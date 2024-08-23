from pydantic import BaseModel, ConfigDict
from typing import List


class LayerResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
