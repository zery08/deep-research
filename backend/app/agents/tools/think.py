"""전략적 반성 도구."""
from langchain_core.tools import tool


@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """Pause and reflect on research progress before deciding next steps.

    Use this tool after each search to analyze what was found and plan next steps.
    This creates a deliberate reasoning step that improves research quality.

    When to use:
    - After receiving search results: What key information did I find?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing gaps: What specific information is still missing?
    - Before concluding: Can I provide a complete, well-sourced answer now?

    Args:
        reflection: Detailed reflection on current findings, gaps, and next steps

    Returns:
        Confirmation that reflection was recorded
    """
    return f"Reflection recorded: {reflection}"
