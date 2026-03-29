from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class SlideType(str, Enum):
    title = "title"
    section = "section"
    content = "content"
    closing = "closing"
    references = "references"


class SlideSource(BaseModel):
    """슬라이드 내용의 출처"""
    source_id: str
    source_name: str
    text: str  # 인용 텍스트
    page: int | None = None


class Slide(BaseModel):
    index: int
    type: SlideType
    title: str
    bullets: list[str] = []
    notes: str = ""  # 발표자 노트
    sources: list[SlideSource] = []


class SlideOutline(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    research_job_id: str
    title: str
    slides: list[Slide] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict) -> "SlideOutline":
        return cls.model_validate(data)


class OutlineRequest(BaseModel):
    research_job_id: str


class OutlineUpdateRequest(BaseModel):
    title: str | None = None
    slides: list[Slide] | None = None


class OutlineResponse(BaseModel):
    id: str
    research_job_id: str
    title: str
    slides: list[Slide]
    created_at: datetime
    updated_at: datetime
