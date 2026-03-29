"""deepagents 기반 리서치 오케스트레이션 서비스."""
import json
from datetime import datetime
from pathlib import Path

from app.agents.prompts import OUTLINE_FILENAME
from app.core.config import settings
from app.core.database import outline_store, research_store, source_store
from app.models.outline import Slide, SlideOutline, SlideSource, SlideType
from app.models.research import ResearchJob, ResearchStatus
from app.models.source import Source


class ResearchService:
    async def create_job(self, topic: str, source_ids: list[str]) -> ResearchJob:
        """리서치 잡을 생성하고 DB에 저장한다."""
        job = ResearchJob(topic=topic, source_ids=source_ids)
        research_store.set(job.id, job.to_dict())
        return job

    async def get_job(self, job_id: str) -> ResearchJob | None:
        data = research_store.get(job_id)
        if not data:
            return None
        return ResearchJob.from_dict(data)

    async def list_jobs(self) -> list[ResearchJob]:
        return [ResearchJob.from_dict(d) for d in research_store.list_all()]

    async def run_research(self, job_id: str) -> None:
        """백그라운드에서 deepagents 리서치 파이프라인을 실행한다."""
        from app.agents.pipeline import create_research_pipeline

        job = await self.get_job(job_id)
        if not job:
            return

        job_dir = settings.jobs_path / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        try:
            await self._set_status(job_id, ResearchStatus.running)

            agent = create_research_pipeline(
                source_ids=job.source_ids,
                job_dir=str(job_dir),
            )

            await agent.ainvoke({
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Research topic: {job.topic}\n\n"
                            f"Source IDs in use: {job.source_ids}\n\n"
                            f"Follow your workflow: plan → retrieve → synthesize → "
                            f"delegate to slide-writer-agent to create the outline."
                        ),
                    }
                ]
            })

            # outline.json 읽어서 DB에 저장
            outline_id = await self._save_outline(job_id, job_dir, job)

            job = await self.get_job(job_id)
            if job:
                job.status = ResearchStatus.done
                job.outline_id = outline_id
                job.updated_at = datetime.utcnow()
                research_store.set(job_id, job.to_dict())

        except Exception as e:
            job = await self.get_job(job_id)
            if job:
                job.status = ResearchStatus.error
                job.error_message = str(e)
                job.updated_at = datetime.utcnow()
                research_store.set(job_id, job.to_dict())
            raise

    async def _save_outline(
        self,
        job_id: str,
        job_dir: Path,
        job: ResearchJob,
    ) -> str | None:
        """outline.json을 읽어 SlideOutline 모델로 파싱 후 DB에 저장한다.

        Returns:
            저장된 outline의 ID, 파일이 없으면 None
        """
        outline_path = job_dir / OUTLINE_FILENAME
        if not outline_path.exists():
            return None

        try:
            data = json.loads(outline_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

        # source_name → source_id 역매핑 구성
        name_to_id: dict[str, str] = {}
        for sid in job.source_ids:
            sdata = source_store.get(sid)
            if sdata:
                name_to_id[Source.from_dict(sdata).name] = sid

        slides = []
        for raw in data.get("slides", []):
            source_refs = raw.get("source_refs", [])
            sources = [
                SlideSource(
                    source_id=name_to_id.get(ref, ""),
                    source_name=ref,
                    text="",
                )
                for ref in source_refs
                if ref
            ]
            try:
                slide_type = SlideType(raw.get("type", "content"))
            except ValueError:
                slide_type = SlideType.content

            slides.append(Slide(
                index=raw.get("index", len(slides) + 1),
                type=slide_type,
                title=raw.get("title", ""),
                bullets=raw.get("bullets", []),
                notes=raw.get("notes", ""),
                sources=sources,
            ))

        outline = SlideOutline(
            research_job_id=job_id,
            title=data.get("title", job.topic),
            slides=slides,
        )
        outline_store.set(outline.id, outline.to_dict())
        return outline.id

    async def _set_status(self, job_id: str, status: ResearchStatus) -> None:
        job = await self.get_job(job_id)
        if job:
            job.status = status
            job.updated_at = datetime.utcnow()
            research_store.set(job_id, job.to_dict())


research_service = ResearchService()
