from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class SourceType(str, Enum):
    pdf = "pdf"
    pptx = "pptx"
    url = "url"


class SourceStatus(str, Enum):
    pending = "pending"
    indexing = "indexing"
    ready = "ready"
    error = "error"


class Source(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: SourceType
    name: str
    original_path: str | None = None  # 업로드 파일 경로 or URL
    status: SourceStatus = SourceStatus.pending
    chunk_count: int = 0
    error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict) -> "Source":
        return cls.model_validate(data)


class SourceCreate(BaseModel):
    """URL 소스 추가 요청"""
    url: str
    name: str | None = None


class SourceResponse(BaseModel):
    id: str
    type: SourceType
    name: str
    status: SourceStatus
    chunk_count: int
    error_message: str | None
    created_at: datetime
