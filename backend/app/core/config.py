from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    # OpenRouter 등 OpenAI 호환 서비스 사용 시 base_url 설정 (없으면 OpenAI 기본값 사용)
    openai_base_url: str | None = Field(None, alias="OPENAI_BASE_URL")
    openai_model: str = "openai/gpt-4o"
    openai_embedding_model: str = "openai/text-embedding-3-small"

    chroma_db_path: str = "./data/chroma"
    upload_dir: str = "./data/uploads"
    parsed_dir: str = "./data/parsed"
    jobs_dir: str = "./data/jobs"

    max_upload_size_mb: int = 50
    chunk_size: int = 800
    chunk_overlap: int = 100

    cors_origins: list[str] = ["http://localhost:5173"]

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)

    @property
    def parsed_path(self) -> Path:
        return Path(self.parsed_dir)

    @property
    def chroma_path(self) -> Path:
        return Path(self.chroma_db_path)

    @property
    def jobs_path(self) -> Path:
        return Path(self.jobs_dir)


settings = Settings()

for _path in [
    settings.upload_path,
    settings.parsed_path,
    settings.chroma_path,
    settings.jobs_path,
]:
    _path.mkdir(parents=True, exist_ok=True)
