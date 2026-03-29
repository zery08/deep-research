"""임베딩 및 ChromaDB 벡터 저장/검색 서비스.

임베딩은 로컬 sentence-transformers 모델을 사용한다.
API 키 불필요, 무료, 오프라인 동작.
"""
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from app.core.config import settings
from app.services.ingestion import ParsedChunk

# 로컬 임베딩 모델 (최초 실행 시 자동 다운로드 ~90MB)
_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingService:
    def __init__(self) -> None:
        self.embeddings = HuggingFaceEmbeddings(
            model_name=_EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        self.vectorstore = Chroma(
            collection_name="deep_research",
            embedding_function=self.embeddings,
            persist_directory=str(settings.chroma_path),
        )

    async def embed_chunks(self, chunks: list[ParsedChunk]) -> int:
        """청크를 임베딩하여 ChromaDB에 저장. 저장된 청크 수 반환."""
        if not chunks:
            return 0

        documents = [
            Document(
                page_content=chunk.text,
                metadata={
                    "source_id": chunk.source_id,
                    "page": chunk.page,
                    **chunk.metadata,
                },
            )
            for chunk in chunks
        ]

        ids = [f"{chunk.source_id}_{i}" for i, chunk in enumerate(chunks)]
        self.vectorstore.add_documents(documents, ids=ids)

        return len(documents)

    async def search(
        self,
        query: str,
        source_ids: list[str],
        k: int = 5,
    ) -> list[dict]:
        """선택된 source_id 내에서만 유사 청크 검색."""
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter={"source_id": {"$in": source_ids}} if source_ids else None,
        )

        return [
            {
                "chunk_id": doc.metadata.get("chunk_id", ""),
                "source_id": doc.metadata.get("source_id", ""),
                "source_name": doc.metadata.get("source_name", ""),
                "text": doc.page_content,
                "page": doc.metadata.get("page"),
                "score": float(score),
            }
            for doc, score in results
        ]

    async def delete_source(self, source_id: str) -> None:
        """소스의 모든 청크를 ChromaDB에서 삭제."""
        self.vectorstore.delete(where={"source_id": source_id})


embedding_service = EmbeddingService()
