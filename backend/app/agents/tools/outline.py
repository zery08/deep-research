"""슬라이드 outline 저장 도구."""
import json
from pathlib import Path

from langchain_core.tools import tool


def make_write_slide_outline_tool(job_dir: str):
    """job_dir가 고정된 write_slide_outline 도구를 생성한다.

    Args:
        job_dir: outline.json을 저장할 절대 경로

    Returns:
        LangChain tool 함수
    """
    @tool(parse_docstring=True)
    def write_slide_outline(outline_json: str) -> str:
        """Save the slide outline JSON to disk. Call this once with the complete outline.

        The JSON must follow this schema:
        {
          "title": "Presentation title",
          "slides": [
            {
              "index": 1,
              "type": "title",
              "title": "Slide title",
              "bullets": ["point 1", "point 2"],
              "notes": "Speaker notes",
              "source_refs": ["filename.pdf p.3"]
            }
          ]
        }

        Slide types: "title", "section", "content", "closing", "references"

        Args:
            outline_json: Complete slide outline as a JSON string

        Returns:
            Confirmation with slide count, or error message
        """
        try:
            data = json.loads(outline_json)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON — {e}"

        if "title" not in data or "slides" not in data:
            return "Error: JSON must have 'title' and 'slides' keys"

        path = Path(job_dir) / "outline.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        slide_count = len(data.get("slides", []))
        return f"Outline saved: {slide_count} slides written to outline.json"

    return write_slide_outline
