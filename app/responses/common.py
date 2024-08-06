from pydantic import BaseModel


# Common 500 error response
class ErrorResponse(BaseModel):
    detail: str
