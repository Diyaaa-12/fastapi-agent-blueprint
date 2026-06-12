from datetime import datetime

from pydantic import Field

from src._core.application.dtos.base_request import BaseRequest
from src._core.application.dtos.base_response import BaseResponse


class PostResponse(BaseResponse):
    id: int
    author_id: int
    author_display_name: str | None = None
    title: str
    body: str
    created_at: datetime
    updated_at: datetime


class CreatePostRequest(BaseRequest):
    author_id: int
    title: str = Field(max_length=255)
    body: str


class UpdatePostRequest(BaseRequest):
    title: str | None = Field(default=None, max_length=255)
    body: str | None = None
