"""PPT 생성 및 다운로드 API."""
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse

from app.core.database import ppt_store, outline_store
from app.core.exceptions import OutlineNotFoundError
from app.models.ppt import PPTJob, PPTStatus, PPTGenerateRequest, PPTResponse
from app.services.ppt_generator import ppt_generator_service

router = APIRouter(prefix="/ppt", tags=["ppt"])


@router.post("/generate", response_model=PPTResponse, status_code=status.HTTP_201_CREATED)
async def generate_ppt(
    request: PPTGenerateRequest,
    background_tasks: BackgroundTasks,
) -> PPTResponse:
    """PPT 생성 시작."""
    outline_data = outline_store.get(request.outline_id)
    if not outline_data:
        raise OutlineNotFoundError(request.outline_id)

    job = PPTJob(outline_id=request.outline_id)
    ppt_store.set(job.id, job.to_dict())

    background_tasks.add_task(ppt_generator_service.generate, job.id)

    return PPTResponse(**job.to_dict())


@router.get("/{job_id}", response_model=PPTResponse)
async def get_ppt_status(job_id: str) -> PPTResponse:
    """PPT 생성 상태 조회."""
    data = ppt_store.get(job_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"PPT job '{job_id}' not found")
    return PPTResponse(**data)


@router.get("/{job_id}/download")
async def download_ppt(job_id: str) -> FileResponse:
    """PPT 파일 다운로드."""
    data = ppt_store.get(job_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"PPT job '{job_id}' not found")

    job = PPTJob.from_dict(data)

    if job.status != PPTStatus.done:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PPT가 아직 생성되지 않았습니다. 현재 상태: {job.status}",
        )

    file_path = Path(job.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PPT 파일을 찾을 수 없습니다.")

    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"presentation_{job_id[:8]}.pptx",
    )
