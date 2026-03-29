import json
from pathlib import Path
from typing import Any
import uuid

from app.core.config import settings


# --- 간단한 JSON 기반 인메모리 스토어 (MVP) ---
# 프로덕션에서는 SQLite 또는 PostgreSQL로 교체


class JSONStore:
    """파일 기반 간단한 KV 스토어. MVP용."""

    def __init__(self, store_path: Path):
        self._path = store_path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("{}")

    def _load(self) -> dict[str, Any]:
        return json.loads(self._path.read_text())

    def _save(self, data: dict[str, Any]) -> None:
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def get(self, key: str) -> Any | None:
        return self._load().get(key)

    def set(self, key: str, value: Any) -> None:
        data = self._load()
        data[key] = value
        self._save(data)

    def delete(self, key: str) -> bool:
        data = self._load()
        if key not in data:
            return False
        del data[key]
        self._save(data)
        return True

    def list_all(self) -> list[Any]:
        return list(self._load().values())

    def generate_id(self) -> str:
        return str(uuid.uuid4())


# 싱글톤 스토어 인스턴스
data_dir = Path("./data")
source_store = JSONStore(data_dir / "db" / "sources.json")
research_store = JSONStore(data_dir / "db" / "research.json")
outline_store = JSONStore(data_dir / "db" / "outlines.json")
ppt_store = JSONStore(data_dir / "db" / "ppts.json")
