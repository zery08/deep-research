# Deep Research PPT Generator

사용자가 업로드한 PDF/PPT 파일과 명시적으로 추가한 URL을 소스로 삼아,
딥 리서치를 수행하고 발표용 슬라이드 초안 및 PPT 파일을 자동 생성하는 웹 애플리케이션.

## 주요 기능

- **파일 업로드**: PDF, PPT/PPTX 파일 업로드 및 인덱싱
- **URL 수집**: 사용자가 명시한 URL에서 콘텐츠 수집
- **소스 기반 딥 리서치**: 선택한 소스 내에서만 근거 수집
- **슬라이드 outline 자동 생성**: 리서치 결과를 슬라이드 구조로 변환
- **PPT 파일 생성 및 다운로드**: 출처 포함 PPTX 자동 생성
- **출처 추적**: 모든 슬라이드 내용에 소스 인용 포함

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | React 18 + TypeScript + Tailwind CSS |
| Backend | FastAPI (Python 3.11+) |
| Agent | LangChain |
| LLM | OpenAI GPT-4o |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | ChromaDB |
| PDF 파싱 | PyMuPDF |
| PPT 파싱/생성 | python-pptx |
| 패키지 관리 | uv (Python) + pnpm (JS) |

## 빠른 시작

### 사전 요구사항
- Python 3.11+
- Node.js 18+
- uv (`pip install uv`)
- pnpm (`npm install -g pnpm`)
- OpenAI API 키

### Backend 실행

```bash
cd backend
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 설정

uv sync
uv run uvicorn app.main:app --reload --port 8000
```

API 문서: http://localhost:8000/docs

### Frontend 실행

```bash
cd frontend
pnpm install
pnpm dev
```

앱: http://localhost:5173

## 사용 방법

1. **소스 추가**: 좌측 패널에서 PDF/PPT 파일 업로드 또는 URL 입력
2. **인덱싱 대기**: 각 소스의 상태가 "준비됨"이 될 때까지 대기
3. **소스 선택**: 리서치에 사용할 소스를 체크박스로 선택
4. **리서치 실행**: 발표 주제를 입력하고 "딥 리서치 시작" 클릭
5. **outline 확인**: 생성된 슬라이드 outline 확인 및 편집
6. **PPT 생성**: "PPT 생성" 버튼 클릭 후 다운로드

## 프로젝트 구조

```
deep-research/
├── backend/
│   ├── app/
│   │   ├── api/          # REST API 라우터
│   │   ├── agents/       # LangChain 에이전트
│   │   ├── core/         # 설정, DB 클라이언트
│   │   ├── models/       # Pydantic 데이터 모델
│   │   └── services/     # 비즈니스 로직
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/   # UI 컴포넌트
│   │   ├── pages/        # 페이지
│   │   ├── hooks/        # 커스텀 훅
│   │   ├── api/          # API 클라이언트
│   │   ├── stores/       # Zustand 스토어
│   │   └── types/        # TypeScript 타입
│   └── package.json
├── plan.md               # 개발 플랜
└── CLAUDE.md             # Claude Code 가이드
```

## 설계 원칙

- **Source-Grounded**: 사용자가 선택한 소스에서만 내용 도출
- **No Hallucination**: RAG 기반으로 근거 없는 내용 생성 억제
- **Traceable**: 모든 슬라이드 내용에 출처 표시
