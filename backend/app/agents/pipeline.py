"""deepagents 기반 리서치 파이프라인 팩토리."""
from langchain_openai import ChatOpenAI

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from app.agents.prompts import ORCHESTRATOR_PROMPT, RETRIEVER_PROMPT, SLIDE_WRITER_PROMPT
from app.agents.tools.retrieval import make_vector_search_tool
from app.agents.tools.outline import make_write_slide_outline_tool
from app.agents.tools.think import think_tool
from app.core.config import settings


def create_research_pipeline(source_ids: list[str], job_dir: str):
    """job별 리서치 에이전트를 생성한다.

    Args:
        source_ids: 검색을 제한할 소스 ID 목록
        job_dir: 에이전트가 outline.json을 저장할 절대 경로

    Returns:
        컴파일된 LangGraph 그래프 (deepagents agent)
    """
    model = ChatOpenAI(
        model=settings.openai_model,
        openai_api_key=settings.openai_api_key,
        temperature=0.0,
        **({"openai_api_base": settings.openai_base_url} if settings.openai_base_url else {}),
    )

    # source_ids가 바인딩된 vector_search 도구
    vector_search = make_vector_search_tool(source_ids)

    # job_dir가 바인딩된 write_slide_outline 도구
    write_slide_outline = make_write_slide_outline_tool(job_dir)

    # 실제 디스크 파일시스템 (job_dir 기준 상대경로 허용, 절대경로도 허용)
    backend = FilesystemBackend(root_dir=job_dir, virtual_mode=False)

    # RetrieverSubAgent: 서브쿼리별 벡터 검색 전담
    retriever_subagent = {
        "name": "retriever-agent",
        "description": (
            "Searches the uploaded source documents for a specific research sub-question. "
            "Give it one focused question at a time. Returns cited findings."
        ),
        "system_prompt": RETRIEVER_PROMPT,
        "tools": [vector_search, think_tool],
    }

    # SlideWriterSubAgent: 리서치 결과 → 슬라이드 outline JSON 저장
    slide_writer_subagent = {
        "name": "slide-writer-agent",
        "description": (
            "Transforms research findings into a structured slide outline JSON and saves it. "
            "Pass the full consolidated research findings and topic."
        ),
        "system_prompt": SLIDE_WRITER_PROMPT,
        "tools": [think_tool, write_slide_outline],
    }

    return create_deep_agent(
        model=model,
        tools=[think_tool],
        system_prompt=ORCHESTRATOR_PROMPT,
        subagents=[retriever_subagent, slide_writer_subagent],
        backend=backend,
        name="research-planner",
    )
