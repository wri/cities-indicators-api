from pydantic import BaseModel


# Common error response
class ErrorResponse(BaseModel):
    detail: str
