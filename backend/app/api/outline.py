"""슬라이드 Outline API."""
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.core.database import outline_store, research_store
from app.core.exceptions import OutlineNotFoundError, ResearchJobNotFoundError
from app.models.outline import OutlineResponse, OutlineUpdateRequest, Slide, SlideOutline
from app.models.research import ResearchJob, ResearchStatus

router = APIRouter(prefix="/outline", tags=["outline"])


@router.post("", response_model=OutlineResponse, status_code=status.HTTP_200_OK)
async def get_or_create_outline(
    request: dict,
) -> OutlineResponse:
    """리서치 잡의 outline을 반환한다.

    에이전트가 리서치 완료 시 outline을 자동 생성하므로,
    이 엔드포인트는 기존에 저장된 outline을 조회하여 반환한다.
    """
    research_job_id = request.get("research_job_id")
    if not research_job_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="research_job_id required")

    research_data = research_store.get(research_job_id)
    if not research_data:
        raise ResearchJobNotFoundError(research_job_id)

    job = ResearchJob.from_dict(research_data)
    if job.status != ResearchStatus.done:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"리서치가 완료되지 않았습니다. 현재 상태: {job.status}",
        )

    if not job.outline_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="에이전트가 outline을 생성하지 못했습니다.",
        )

    data = outline_store.get(job.outline_id)
    if not data:
        raise OutlineNotFoundError(job.outline_id)

    return OutlineResponse(**data)


@router.get("/{outline_id}", response_model=OutlineResponse)
async def get_outline(outline_id: str) -> OutlineResponse:
    """Outline 조회."""
    data = outline_store.get(outline_id)
    if not data:
        raise OutlineNotFoundError(outline_id)
    return OutlineResponse(**data)


@router.put("/{outline_id}", response_model=OutlineResponse)
async def update_outline(outline_id: str, request: OutlineUpdateRequest) -> OutlineResponse:
    """Outline 수정."""
    data = outline_store.get(outline_id)
    if not data:
        raise OutlineNotFoundError(outline_id)

    outline = SlideOutline.from_dict(data)
    if request.title is not None:
        outline.title = request.title
    if request.slides is not None:
        outline.slides = request.slides
    outline.updated_at = datetime.utcnow()

    outline_store.set(outline_id, outline.to_dict())
    return OutlineResponse(**outline.to_dict())
