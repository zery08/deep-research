# Deep Research PPT Generator — 프로젝트 플랜

## 프로젝트 개요

사용자가 업로드한 PDF/PPT 파일과 명시적으로 추가한 URL을 소스로 삼아,
**deepagents 라이브러리** 기반의 딥 리서치를 수행하고
발표용 슬라이드 초안 및 PPT 파일을 자동 생성하는 웹 애플리케이션.

---

## 핵심 기술: deepagents 라이브러리

deepagents는 LangChain이 만든 "batteries-included" 에이전트 하네스다.
`create_deep_agent()`가 **LangGraph 기반의 컴파일된 그래프**를 반환한다.

### 내장 기능 (별도 구현 불필요)
- `write_todos`: 태스크 플래닝 및 진행 추적
- `task`: 서브에이전트에 작업 위임 (격리된 컨텍스트)
- `read_file`, `write_file`: 에이전트가 결과를 파일로 저장/읽기
- Context management: 대화가 길어지면 자동 요약

### 우리가 직접 구현하는 커스텀 도구
```python
@tool(parse_docstring=True)
def vector_search(query: str, source_ids: list[str]) -> str:
    """선택된 소스 내에서 관련 청크를 검색한다."""
    # ChromaDB 벡터 검색, source_id 필터링

@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """리서치 진행 상황을 점검하고 다음 단계를 계획한다."""

@tool(parse_docstring=True)
def write_slide_outline(outline_json: str) -> str:
    """슬라이드 outline을 JSON 파일로 저장한다."""
```

---

## 아키텍처 개요

```
[Frontend - React]
  ├── SourceManager: 파일 업로드, URL 추가, 소스 목록/선택
  ├── ResearchPanel: 리서치 주제 입력, 실행, 진행 상태 (SSE)
  ├── OutlineEditor: 슬라이드 outline 확인 및 편집
  └── SlidePreview: PPT 미리보기 및 다운로드

[Backend - FastAPI]
  ├── Ingestion API: 파일 업로드, URL 크롤링
  ├── Parsing Layer: PDF/PPT → 텍스트 청크
  ├── Embedding Layer: OpenAI Embeddings → ChromaDB
  ├── Research API: deepagents OrchestratorAgent 실행 (백그라운드)
  ├── Outline API: 에이전트 결과 → SlideOutline 모델
  └── PPT API: SlideOutline → PPTX 파일 생성

[Agent Layer - deepagents]
  OrchestratorAgent (create_deep_agent)
    built-in: write_todos, task, read_file, write_file
    custom: vector_search, think_tool
    subagents:
      ├── RetrieverSubAgent
      │     custom: vector_search, think_tool
      └── SlideWriterSubAgent
            custom: think_tool, write_slide_outline

[Storage]
  ├── /data/uploads: 업로드 원본 파일
  ├── /data/parsed: 파싱된 청크 JSON
  ├── /data/jobs/{job_id}/: 에이전트 작업 파일 공간
  └── ChromaDB: 임베딩 벡터 + 메타데이터
```

---

## 데이터 플로우

```
[사용자 액션]
  1. 파일 업로드 / URL 추가
        ↓
  2. 파싱 + 청킹 + 임베딩 → ChromaDB (source_id 태깅)
        ↓
  3. 소스 선택 + 리서치 주제 입력
        ↓
  4. OrchestratorAgent 실행 (백그라운드)
     └── write_todos: 주제 → [서브쿼리 목록]
     └── task → RetrieverSubAgent × N (병렬)
           └── vector_search(query, source_ids=[...]) → 관련 청크
           └── think_tool → 진행 점검
     └── 수집된 청크 종합 → 섹션별 요약
     └── task → SlideWriterSubAgent
           └── think_tool → 구조 설계
           └── write_slide_outline(json) → outline 파일 저장
        ↓
  5. 에이전트 완료 → outline JSON 파싱 → DB 저장
        ↓
  6. PPTGenerator: outline → .pptx 파일 생성
        ↓
  7. 사용자: 미리보기 → 다운로드
```

---

## 데이터 모델

### Source
```json
{
  "id": "uuid",
  "type": "pdf | pptx | url",
  "name": "파일명 or URL",
  "status": "pending | indexing | ready | error",
  "chunk_count": 42,
  "created_at": "ISO8601"
}
```

### ResearchJob
```json
{
  "id": "uuid",
  "topic": "사용자 리서치 주제",
  "source_ids": ["uuid1", "uuid2"],
  "status": "pending | running | done | error",
  "agent_log": "에이전트 실행 로그 (SSE로 스트리밍)",
  "outline_id": "uuid | null",
  "created_at": "ISO8601"
}
```

### SlideOutline
```json
{
  "id": "uuid",
  "research_job_id": "uuid",
  "title": "발표 제목",
  "slides": [
    {
      "index": 1,
      "title": "슬라이드 제목",
      "type": "title | content | section | closing | references",
      "bullets": ["내용1", "내용2"],
      "notes": "발표자 노트",
      "sources": [
        {"source_id": "uuid", "chunk_id": "str", "text": "인용 텍스트", "page": 3}
      ]
    }
  ]
}
```

---

## 단계별 개발 계획

### Phase 0: 초기화 (완료)
- [x] plan.md 작성
- [x] CLAUDE.md 작성
- [x] README.md 작성
- [x] 폴더 구조 설계

### Phase 1: Ingestion & 인덱싱 (1주차)
- [ ] FastAPI 기본 서버 + 설정 (pydantic-settings)
- [ ] Source Pydantic 모델 정의
- [ ] PDF 파싱 서비스 (PyMuPDF)
- [ ] PPT 파싱 서비스 (python-pptx)
- [ ] URL 크롤링 서비스 (httpx + BeautifulSoup4)
- [ ] 텍스트 청킹 (LangChain RecursiveCharacterTextSplitter)
- [ ] 임베딩 + ChromaDB 저장
- [ ] Source API 라우터 (upload, url, list, delete, status)
- [ ] React 소스 관리 UI

### Phase 2: deepagents 파이프라인 (2주차)
- [ ] `vector_search` 커스텀 도구 구현
- [ ] `think_tool` 구현
- [ ] `write_slide_outline` 구현
- [ ] RetrieverSubAgent 시스템 프롬프트 작성
- [ ] SlideWriterSubAgent 시스템 프롬프트 작성
- [ ] OrchestratorAgent (`create_deep_agent`) 조립
- [ ] ResearchJob 모델 + DB
- [ ] Research API (POST /api/research, GET, SSE stream)
- [ ] 에이전트 백그라운드 실행 + SSE 상태 전달
- [ ] React 리서치 패널 UI

### Phase 3: Outline & PPT 생성 (3주차)
- [ ] SlideOutline Pydantic 모델 정의
- [ ] 에이전트 결과 파일 → SlideOutline JSON 파싱
- [ ] Outline API (GET, PUT)
- [ ] python-pptx 기반 PPTGenerator 서비스
- [ ] 출처 슬라이드 자동 생성 로직
- [ ] PPT API (generate, download)
- [ ] React outline 편집기 UI
- [ ] React 슬라이드 미리보기
- [ ] 다운로드 기능

### Phase 4: 품질 개선 (4주차)
- [ ] Source-grounded 검증 강화
- [ ] 에러 핸들링 전면 점검
- [ ] 긴 리서치 타임아웃 처리
- [ ] UX 개선 (진행률, 에러 메시지)

---

## 기술 스택

| 레이어 | 기술 | 선택 이유 |
|--------|------|-----------|
| Frontend | React 18 + TypeScript | 컴포넌트 재사용, 타입 안전성 |
| Frontend UI | Tailwind CSS + shadcn/ui | 빠른 프로토타이핑 |
| Backend | FastAPI | async 지원, 자동 문서화 |
| Agent | **deepagents** | batteries-included, subagent 지원, LangGraph 기반 |
| LLM | OpenAI GPT-4o | 강력한 요약/구조화 능력 |
| Embeddings | OpenAI text-embedding-3-small | 비용 효율적 |
| Vector DB | ChromaDB | 로컬 설치 간편, source_id 필터링 지원 |
| PDF 파싱 | PyMuPDF (fitz) | 빠르고 정확한 텍스트 추출 |
| PPT 파싱/생성 | python-pptx | 표준 라이브러리 |
| URL 크롤링 | httpx + BeautifulSoup4 | 비동기 HTTP, HTML 파싱 |
| 패키지 관리 | uv (Python) + pnpm (JS) | 속도 |

---

## 리스크 및 고려사항

1. **deepagents 파일 공간**: 에이전트가 `write_file`로 임시 파일을 생성함 → job별 격리 디렉토리 필요
2. **LLM 비용**: Orchestrator + 여러 SubAgent 호출 → 토큰 사용량 모니터링 필요
3. **vector_search InjectedToolArg**: `source_ids`는 사용자가 선택한 값을 서버에서 주입해야 함 (에이전트가 임의로 변경 불가)
4. **청킹 전략**: chunk 크기와 overlap이 검색 품질에 직결 → 800/100 기본값, 튜닝 가능하게 설정화
5. **PPT 디자인**: python-pptx는 디자인 자유도 제한 → 기본 템플릿 사용
6. **긴 리서치 시간**: deepagents는 여러 번 LLM 호출 → SSE로 진행 상태 실시간 표시 필수
