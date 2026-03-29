from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class PPTStatus(str, Enum):
    pending = "pending"
    generating = "generating"
    done = "done"
    error = "error"


class PPTJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    outline_id: str
    status: PPTStatus = PPTStatus.pending
    file_path: str | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict) -> "PPTJob":
        return cls.model_validate(data)


class PPTGenerateRequest(BaseModel):
    outline_id: str


class PPTResponse(BaseModel):
    id: str
    outline_id: str
    status: PPTStatus
    error_message: str | None
    created_at: datetime
