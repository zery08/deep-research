from pathlib import Path

import pytest

from app.agents.prompts import FINAL_REPORT_PATH
from app.agents.tools.think import think_tool
from app.services import research as research_module
import app.agents.pipeline as pipeline_module


class _FakeStore:
    def __init__(self) -> None:
        self._data: dict[str, dict] = {}

    def set(self, key: str, value: dict) -> None:
        self._data[key] = value

    def get(self, key: str) -> dict | None:
        return self._data.get(key)

    def list_all(self) -> list[dict]:
        return list(self._data.values())


def test_create_research_pipeline_restricts_retrieval_to_subagent(monkeypatch, tmp_path: Path) -> None:
    captured: dict = {}
    fake_model = object()
    fake_vector_search = object()

    monkeypatch.setattr(pipeline_module, "_create_model", lambda: fake_model)
    monkeypatch.setattr(pipeline_module, "make_vector_search_tool", lambda source_ids: fake_vector_search)

    def _fake_create_deep_agent(**kwargs):
        captured.update(kwargs)
        return "compiled-agent"

    monkeypatch.setattr(pipeline_module, "create_deep_agent", _fake_create_deep_agent)

    agent = pipeline_module.create_research_pipeline(["source-1"], str(tmp_path))

    assert agent == "compiled-agent"
    assert captured["model"] is fake_model
    assert captured["tools"] == []

    backend = captured["backend"]
    assert isinstance(backend, pipeline_module.FilesystemBackend)
    assert backend.virtual_mode is True
    assert backend.cwd == tmp_path.resolve()

    subagents = {subagent["name"]: subagent for subagent in captured["subagents"]}
    assert set(subagents) == {"general-purpose", "retriever-agent"}
    assert subagents["general-purpose"]["tools"] == []
    assert "must not be used for factual research" in subagents["general-purpose"]["description"]
    assert subagents["retriever-agent"]["tools"] == [fake_vector_search, think_tool]
    assert subagents["retriever-agent"]["model"] is fake_model
    assert FINAL_REPORT_PATH in captured["system_prompt"]
    assert "{final_report_path}" not in captured["system_prompt"]


@pytest.mark.asyncio
async def test_run_research_uses_workspace_report_path(monkeypatch, tmp_path: Path) -> None:
    fake_store = _FakeStore()
    captured: dict = {}

    monkeypatch.setattr(research_module, "research_store", fake_store)
    monkeypatch.setattr(research_module.settings, "jobs_dir", str(tmp_path))

    class _FakeAgent:
        def __init__(self, job_dir: str) -> None:
            self.job_dir = Path(job_dir)
            self.payloads: list[dict] = []

        async def ainvoke(self, payload: dict) -> dict:
            self.payloads.append(payload)
            (self.job_dir / "final_report.md").write_text("report body", encoding="utf-8")
            return {"messages": []}

    def _fake_create_research_pipeline(source_ids: list[str], job_dir: str):
        captured["source_ids"] = source_ids
        captured["job_dir"] = job_dir
        captured["agent"] = _FakeAgent(job_dir)
        return captured["agent"]

    monkeypatch.setattr(pipeline_module, "create_research_pipeline", _fake_create_research_pipeline)

    service = research_module.ResearchService()
    job = await service.create_job(topic="Deep agents", source_ids=["source-1"])

    await service.run_research(job.id)

    payload = captured["agent"].payloads[0]
    prompt = payload["messages"][0]["content"]

    assert FINAL_REPORT_PATH in prompt
    assert str(tmp_path) not in prompt

    saved_job = fake_store.get(job.id)
    assert saved_job is not None
    assert saved_job["result_file"] == str(tmp_path / job.id / "final_report.md")
    assert saved_job["summary"] == "report body"
