from pydantic import BaseModel, ConfigDict


class LayerResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
