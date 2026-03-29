# CLAUDE.md

이 파일은 Claude Code가 이 레포지토리에서 작업할 때의 가이드라인을 제공합니다.

## 프로젝트 개요

**딥리서치 기반 PPT 자동 생성 웹앱**

사용자가 업로드한 PDF/PPT 파일과 명시적으로 추가한 URL을 소스로 삼아,
`deepagents` 라이브러리 기반의 딥 리서치를 수행하고
발표용 슬라이드 초안 및 PPT 파일을 자동 생성하는 웹 애플리케이션.

---

## 핵심: deepagents 라이브러리

이 프로젝트의 에이전트 레이어는 **LangChain deepagents 라이브러리**를 사용한다.
(`reference/deepagents/` 에 레포 클론이 있으니 구현 전 반드시 참고할 것)

### deepagents의 핵심 패턴

```python
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

agent = create_deep_agent(
    model=init_chat_model("openai:gpt-4o"),
    tools=[my_custom_tool],          # LangChain @tool 데코레이터 함수
    system_prompt="...",
    subagents=[sub_agent_config],    # dict: name, description, system_prompt, tools
)

result = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
```

### 내장 도구 (별도 구현 불필요)
- `write_todos` — 태스크 플래닝 및 TODO 목록 관리
- `read_file`, `write_file`, `edit_file`, `ls`, `glob`, `grep` — 파일 시스템
- `execute` — 셸 명령 실행 (샌드박스)
- `task` — 서브에이전트에 작업 위임 (격리된 컨텍스트 윈도우)

### 우리 프로젝트의 에이전트 구조

```
OrchestratorAgent (create_deep_agent)
  └── tools: [vector_search, think_tool, write_slide_outline]
  └── subagents:
       ├── RetrieverSubAgent
       │     tools: [vector_search, think_tool]
       │     역할: 서브쿼리별 벡터 검색, 근거 청크 수집
       └── SlideWriterSubAgent
             tools: [think_tool, write_slide_outline]
             역할: 수집된 근거 → 슬라이드 outline JSON 생성
```

### 커스텀 도구 (우리가 직접 구현)
| 도구 | 파일 | 역할 |
|------|------|------|
| `vector_search` | `agents/tools/retrieval.py` | ChromaDB에서 선택된 source_id 범위 내 벡터 검색 |
| `think_tool` | `agents/tools/think.py` | 리서치 진행 상태 점검 및 전략적 반성 |
| `write_slide_outline` | `agents/tools/outline.py` | 슬라이드 outline JSON을 파일에 기록 |

### 중요 제약
- **web search 도구 추가 금지**: 소스는 사용자가 명시적으로 추가한 것만 사용
- `vector_search`는 항상 `source_ids` 파라미터로 필터링하여 선택된 소스만 검색
- 에이전트가 생성하는 모든 내용은 검색된 청크에 근거해야 함 (system_prompt로 강제)

---

## 폴더 구조

```
deep-research/
├── backend/               # FastAPI 백엔드
│   ├── app/
│   │   ├── api/           # API 라우터 (routes)
│   │   ├── agents/        # deepagents 기반 에이전트
│   │   │   ├── tools/     # 커스텀 LangChain 도구
│   │   │   ├── prompts/   # 에이전트별 시스템 프롬프트
│   │   │   └── pipeline.py  # OrchestratorAgent 조립
│   │   ├── core/          # 설정, DB, 유틸
│   │   ├── models/        # Pydantic 모델
│   │   ├── services/      # 비즈니스 로직 서비스
│   │   └── main.py        # FastAPI 앱 진입점
│   ├── tests/
│   ├── pyproject.toml
│   └── .env.example
├── frontend/              # React 프론트엔드
│   ├── src/
│   │   ├── components/    # UI 컴포넌트
│   │   ├── pages/         # 페이지 컴포넌트
│   │   ├── hooks/         # 커스텀 훅
│   │   ├── api/           # API 클라이언트
│   │   ├── stores/        # 상태 관리 (Zustand)
│   │   └── types/         # TypeScript 타입
│   ├── package.json
│   └── vite.config.ts
├── reference/
│   └── deepagents/        # deepagents 레포 (참고용)
├── plan.md
├── README.md
└── CLAUDE.md
```

---

## 개발 명령어

### Backend
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
uv run pytest
```

### Frontend
```bash
cd frontend
pnpm install
pnpm dev          # port 5173
pnpm build
pnpm test
```

---

## API 엔드포인트 구조

```
POST   /api/sources/upload          # 파일 업로드
POST   /api/sources/url             # URL 추가
GET    /api/sources                 # 소스 목록
DELETE /api/sources/{id}            # 소스 삭제
GET    /api/sources/{id}/status     # 인덱싱 상태

POST   /api/research                # 리서치 시작 (deepagents 실행)
GET    /api/research/{id}           # 리서치 상태/결과
GET    /api/research/{id}/stream    # SSE 스트림

POST   /api/outline                 # outline 생성
GET    /api/outline/{id}            # outline 조회
PUT    /api/outline/{id}            # outline 수정

POST   /api/ppt/generate            # PPT 생성
GET    /api/ppt/{id}/download       # PPT 다운로드
```

---

## 핵심 설계 원칙

1. **Source-Grounded 응답만 허용**: 에이전트 시스템 프롬프트에서 "반드시 검색된 청크에서만 내용 도출"을 명시. 임의 생성 금지.
2. **Source 추적 필수**: 모든 슬라이드 내용은 `source_id + chunk_id` 기반 출처를 포함해야 함.
3. **단계 분리**: Ingestion → Retrieval → Research → Outline → PPT Generation 각 단계의 입출력 명확히 분리.
4. **비동기 처리**: 파싱, 임베딩, 리서치, PPT 생성은 모두 비동기 백그라운드 태스크로 처리하고 SSE로 상태 전달.
5. **deepagents 패턴 준수**: `create_deep_agent` + subagents 패턴으로 구성. 직접 LangChain chain 작성 불필요.

---

## 코드 스타일 가이드

### Python (Backend)
- Python 3.11+
- 타입 힌트 필수 (모든 함수 파라미터, 반환값)
- Pydantic v2 모델 사용
- async/await 기반 작성
- 서비스 계층과 라우터 계층 분리 (라우터는 얇게, 로직은 서비스에)
- 에러는 커스텀 예외 클래스로 관리
- Google-style docstring 사용
- `@tool(parse_docstring=True)` 패턴으로 도구 정의

### TypeScript (Frontend)
- React 18 + TypeScript strict mode
- 함수형 컴포넌트 + 훅
- Zustand로 전역 상태 관리
- React Query (TanStack Query)로 서버 상태 관리
- 컴포넌트는 작게 유지, 복잡 로직은 훅으로 분리

---

## 환경 변수

```env
# backend/.env
OPENAI_API_KEY=sk-...
CHROMA_DB_PATH=./data/chroma
UPLOAD_DIR=./data/uploads
PARSED_DIR=./data/parsed
MAX_UPLOAD_SIZE_MB=50
CHUNK_SIZE=800
CHUNK_OVERLAP=100
CORS_ORIGINS=["http://localhost:5173"]
```

---

## 주의사항

- `vector_search` 도구에는 항상 `source_ids` 파라미터를 주입하여 선택된 소스만 검색.
- ChromaDB 컬렉션은 source_id로 필터링.
- PPT 생성 시 출처 슬라이드(마지막 슬라이드)를 항상 포함.
- 긴 작업(리서치, PPT 생성)은 FastAPI 백그라운드 태스크로 처리하고 job_id로 폴링.
- deepagents의 파일시스템 도구(`write_file` 등)는 에이전트가 리서치 결과를 임시 파일에 저장하는 데 활용됨.
