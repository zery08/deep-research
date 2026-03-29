"""소스 관리 API."""
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, status

from app.core.config import settings
from app.core.database import source_store
from app.core.exceptions import SourceNotFoundError, FileTooLargeError, UnsupportedFileTypeError
from app.models.source import Source, SourceType, SourceStatus, SourceCreate, SourceResponse
from app.services.ingestion import ingestion_service
from app.services.embedding import embedding_service

router = APIRouter(prefix="/sources", tags=["sources"])

ALLOWED_EXTENSIONS = {".pdf", ".ppt", ".pptx"}
MAX_BYTES = settings.max_upload_size_mb * 1024 * 1024


async def _index_source(source_id: str) -> None:
    """백그라운드 인덱싱 태스크."""
    data = source_store.get(source_id)
    if not data:
        return

    source = Source.from_dict(data)
    source.status = SourceStatus.indexing
    source_store.set(source_id, source.to_dict())

    try:
        chunks = await ingestion_service.parse_and_chunk(source)
        chunk_count = await embedding_service.embed_chunks(chunks)

        source.status = SourceStatus.ready
        source.chunk_count = chunk_count
        source_store.set(source_id, source.to_dict())

    except Exception as e:
        source.status = SourceStatus.error
        source.error_message = str(e)
        source_store.set(source_id, source.to_dict())


@router.post("/upload", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> SourceResponse:
    """PDF 또는 PPT/PPTX 파일 업로드."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"지원하지 않는 파일 형식입니다. 허용: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"파일 크기가 {settings.max_upload_size_mb}MB를 초과합니다.",
        )

    source_type = SourceType.pdf if suffix == ".pdf" else SourceType.pptx
    source = Source(
        type=source_type,
        name=file.filename or "unknown",
    )

    # 파일 저장
    save_path = settings.upload_path / f"{source.id}{suffix}"
    save_path.write_bytes(content)
    source.original_path = str(save_path)

    source_store.set(source.id, source.to_dict())
    background_tasks.add_task(_index_source, source.id)

    return SourceResponse(**source.to_dict())


@router.post("/url", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def add_url(
    request: SourceCreate,
    background_tasks: BackgroundTasks,
) -> SourceResponse:
    """URL 소스 추가."""
    source = Source(
        type=SourceType.url,
        name=request.name or request.url,
        original_path=request.url,
    )
    source_store.set(source.id, source.to_dict())
    background_tasks.add_task(_index_source, source.id)
    return SourceResponse(**source.to_dict())


@router.get("", response_model=list[SourceResponse])
async def list_sources() -> list[SourceResponse]:
    """소스 목록 조회."""
    sources = [Source.from_dict(d) for d in source_store.list_all()]
    sources.sort(key=lambda s: s.created_at, reverse=True)
    return [SourceResponse(**s.to_dict()) for s in sources]


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(source_id: str) -> SourceResponse:
    """소스 상태 조회."""
    data = source_store.get(source_id)
    if not data:
        raise SourceNotFoundError(source_id)
    return SourceResponse(**data)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(source_id: str) -> None:
    """소스 삭제 (파일 + 벡터 포함)."""
    data = source_store.get(source_id)
    if not data:
        raise SourceNotFoundError(source_id)

    source = Source.from_dict(data)

    # 업로드 파일 삭제
    if source.original_path and source.type != SourceType.url:
        path = Path(source.original_path)
        if path.exists():
            path.unlink()

    # 벡터 삭제
    await embedding_service.delete_source(source_id)

    source_store.delete(source_id)
