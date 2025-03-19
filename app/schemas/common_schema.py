from enum import Enum

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class ApplicationIdParam(str, Enum):
    ccl = "ccl"
    cid = "cid"
