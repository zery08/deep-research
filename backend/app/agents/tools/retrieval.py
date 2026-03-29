"""벡터 검색 도구: 선택된 소스 내에서만 검색."""
from langchain_core.tools import tool


def make_vector_search_tool(source_ids: list[str]):
    """source_ids가 고정된 vector_search 도구를 생성한다.

    에이전트가 임의로 검색 범위를 변경하지 못하도록
    source_ids를 클로저로 바인딩한다.

    Args:
        source_ids: 검색을 제한할 소스 ID 목록

    Returns:
        LangChain tool 함수
    """
    @tool(parse_docstring=True)
    def vector_search(query: str, k: int = 6) -> str:
        """Search for relevant text chunks from selected source documents.

        Use this tool to find information from the user's uploaded documents and URLs.
        All searches are restricted to the pre-selected sources only.

        Args:
            query: Specific search query to find relevant information
            k: Number of results to return (default 6, max 10)

        Returns:
            Formatted search results with source attribution and page numbers
        """
        # Lazy import to avoid loading the vector store during module import.
        from app.services.embedding import embedding_service

        k = min(k, 10)
        results = embedding_service.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter={"source_id": {"$in": source_ids}} if source_ids else None,
        )

        if not results:
            return f"No results found for query: '{query}'"

        formatted = []
        for doc, score in results:
            meta = doc.metadata
            page_info = f"page {meta['page']}" if meta.get("page") else "N/A"
            formatted.append(
                f"### [{meta.get('source_name', 'Unknown')}] ({page_info})\n"
                f"{doc.page_content}\n"
                f"*(source_id: {meta.get('source_id', '')}, relevance: {score:.3f})*"
            )

        return f"Found {len(results)} result(s) for '{query}':\n\n" + "\n\n---\n\n".join(formatted)

    return vector_search
