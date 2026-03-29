"""리서치 API."""
import asyncio
from fastapi import APIRouter, BackgroundTasks, status

from app.core.exceptions import ResearchJobNotFoundError
from app.models.research import ResearchRequest, ResearchResponse
from app.services.research import research_service

router = APIRouter(prefix="/research", tags=["research"])


@router.post("", response_model=ResearchResponse, status_code=status.HTTP_201_CREATED)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
) -> ResearchResponse:
    """딥 리서치 시작."""
    job = await research_service.create_job(
        topic=request.topic,
        source_ids=request.source_ids,
    )
    background_tasks.add_task(research_service.run_research, job.id)
    return ResearchResponse(**job.to_dict())


@router.get("", response_model=list[ResearchResponse])
async def list_research_jobs() -> list[ResearchResponse]:
    """리서치 목록 조회."""
    jobs = await research_service.list_jobs()
    jobs.sort(key=lambda j: j.created_at, reverse=True)
    return [ResearchResponse(**j.to_dict()) for j in jobs]


@router.get("/{job_id}", response_model=ResearchResponse)
async def get_research(job_id: str) -> ResearchResponse:
    """리서치 상태 및 결과 조회."""
    job = await research_service.get_job(job_id)
    if not job:
        raise ResearchJobNotFoundError(job_id)
    return ResearchResponse(**job.to_dict())
