from datetime import datetime
from enum import Enum

import uuid
from pydantic import BaseModel, Field


class ResearchStatus(str, Enum):
    pending = "pending"
    running = "running"   # deepagents 에이전트 실행 중
    done = "done"
    error = "error"


class ResearchJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    source_ids: list[str]
    status: ResearchStatus = ResearchStatus.pending
    # deepagents가 write_file로 저장한 결과 파일 경로
    result_file: str | None = None
    # 에이전트 최종 리포트 텍스트 (outline 생성에 사용)
    summary: str = ""
    outline_id: str | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict) -> "ResearchJob":
        return cls.model_validate(data)


class ResearchRequest(BaseModel):
    topic: str
    source_ids: list[str]


class ResearchResponse(BaseModel):
    id: str
    topic: str
    source_ids: list[str]
    status: ResearchStatus
    outline_id: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
