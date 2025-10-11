# Notes Web Application Project Plan

## 1. 프로젝트 비전
웹 브라우저에서 개인 노트를 작성·저장하고, 해시태그 기반으로 빠르게 검색할 수 있는 경량 노트 애플리케이션을 구축합니다. 사용자는 다양한 디바이스에서 접근 가능하며, 직관적인 UI와 강력한 필터링 기능을 제공하는 것이 목표입니다.

## 2. 주요 기능 요구 사항
- **노트 작성 및 편집**: 마크다운 지원, 자동 저장, 버전 관리(히스토리 보기) 옵션.
- **해시태그 관리**: 노트당 다수의 해시태그, 자동 완성, 빈도 기반 추천.
- **검색 및 필터링**: 해시태그, 키워드, 생성/수정일, 즐겨찾기 여부로 검색.
- **생성형 AI 대화 인사이트 추출**: ChatGPT 등에서 복합 질문 대화를 가져와 문맥별 핵심 질문/응답을 자동 요약하고 노트 제목·본문·태그와 연동하여 검색성을 강화.
- **정렬 및 정리**: 최근 작성/수정 순, 알파벳, 커스텀 폴더링.
- **사용자 계정**: 이메일 기반 가입/로그인, OAuth 2.0 확장 고려.
- **데이터 동기화**: 디바이스 간 동기화, 백업/복원 API.
- **알림/리마인더(선택)**: 특정 노트를 일정에 맞춰 리마인드.

## 3. 기술 스택 제안
- **백엔드**: Python 3.11+, FastAPI
- **프론트엔드**: React 18 + TypeScript, Vite 기반 빌드
- **데이터베이스**: PostgreSQL 18 (개발 환경에서는 SQLite 가능)
- **ORM/데이터 계층**: SQLModel 또는 SQLAlchemy + Pydantic 모델
- **인증/인가**: JWT 기반 토큰 관리, OAuth2 Password Flow
- **AI 서비스 연동**: OpenAI API 또는 Azure OpenAI, 임베딩은 pgvector 기반 저장
- **배포 환경**: Docker Compose, 이후 Kubernetes 확장 고려
- **테스팅**: Pytest, Playwright(E2E), Storybook(컴포넌트)
- **CI/CD**: GitHub Actions 기반 테스트 및 배포 파이프라인

## 4. 시스템 아키텍처 개요
```
[Browser] --REST/JSON--> [FastAPI Backend] --ORM--> [PostgreSQL]
                              |
                              +--> [Redis (선택적 캐시 및 세션 관리)]
```
- **API 서버**: 인증, 노트 CRUD, 해시태그 관리, 검색 기능을 제공.
- **프론트엔드 SPA**: React 기반으로 FastAPI와 통신하며 UI 제공.
- **데이터베이스**: PostgreSQL 18 + pgvector 확장으로 구조화/비정형 데이터와 임베딩을 함께 저장.
- **실시간 기능(선택)**: 웹소켓을 통한 동시 편집/라이브 업데이트 고려.

## 5. 데이터 모델 초안
- **User**: id, email, password_hash, name, created_at, updated_at
- **Note**: id, user_id, title, content(markdown), is_favorite, created_at, updated_at
- **Tag**: id, name, created_at
- **NoteTag**: note_id, tag_id (다대다 관계)
- **ConversationThread**: id, user_id, source (chatgpt 등), external_url, captured_at
- **ConversationChunk**: id, thread_id, role, content, sequence, embedding_vector, keywords, created_at
- **Insight**: id, note_id, thread_id, chunk_ids, summary, key_questions, action_items, created_at
- **Reminder (선택)**: id, note_id, remind_at, status

## 6. API 엔드포인트 설계 초안
| 메서드 | 경로 | 설명 |
| ------ | ---- | ---- |
| POST | /auth/register | 사용자 등록 |
| POST | /auth/login | 로그인 및 JWT 발급 |
| GET | /notes | 노트 목록 조회 (필터/검색 쿼리 지원) |
| POST | /notes | 노트 생성 |
| GET | /notes/{id} | 노트 상세 조회 |
| PATCH | /notes/{id} | 노트 수정 |
| DELETE | /notes/{id} | 노트 삭제 |
| GET | /tags | 태그 목록 및 추천 |
| POST | /tags | 태그 생성 |
| GET | /tags/popular | 인기 태그 조회 |
| POST | /notes/{id}/favorite | 즐겨찾기 설정 |
| POST | /conversations/import | 생성형 AI 대화 로그 수집 및 스레드 생성 |
| GET | /conversations/{id}/insights | 대화에서 추출된 요약·핵심 질문 조회 |
| POST | /notes/{id}/insights | 선택한 노트에 대화 인사이트 연동 |
| GET | /reminders | 리마인더 목록 (선택) |

## 7. 초기 개발 단계 로드맵
1. **프로젝트 초기화 (스프린트 0)**
   - FastAPI + Poetry/UV 기반 백엔드 스캐폴딩
   - React + Vite 템플릿 생성
   - Docker Compose로 개발 환경 통합
2. **기본 인증 및 사용자 관리 (스프린트 1)**
   - 사용자 모델/마이그레이션
   - 가입/로그인 API 및 JWT 발급
   - 프론트엔드 로그인/회원가입 UI
3. **노트 CRUD 및 태그 시스템 (스프린트 2)**
   - 노트/태그 데이터 모델, API 구현
   - 해시태그 자동완성 로직, 프론트엔드 태그 UI
4. **검색 및 필터링 (스프린트 3)**
   - 텍스트 검색, 필터링, 정렬 API
   - UI에서 다중 조건 검색 제공
5. **생성형 AI 대화 인사이트 (스프린트 4)**
   - 대화 업로드 API, LLM 기반 요약/질문 추출 파이프라인 구축
   - pgvector를 활용한 의미 검색 및 노트 연결 UX 구현
6. **사용성 향상 기능 (스프린트 5)**
   - 즐겨찾기, 노트 히스토리, 리마인더 도입 여부 결정
   - 접근성 개선, 다크모드 등 UI 폴리싱
7. **테스팅 & 배포 (스프린트 6)**
   - 단위/통합 테스트 확대, CI 파이프라인 구축
   - 프로덕션 배포 전략 수립 (예: Railway, Render, AWS ECS)

## 8. 생성형 AI 대화 인사이트 기능 설계
1. **대화 캡처 경로 정의**
   - ChatGPT 등 외부 생성형 AI UI에서 복사한 대화를 브라우저 확장 또는 웹 입력 폼을 통해 업로드.
   - 자동 캡처를 위해 브라우저 확장(추후) 또는 데스크톱 앱 연동 고려.
2. **대화 전처리 및 분리**
   - 역할(role)과 순번(sequence)을 기준으로 발화 단위를 `ConversationChunk`로 분해.
   - 문장 내 다중 질문을 LLM(예: GPT-4)으로 재분류하여 핵심 질문·응답 쌍을 파악.
3. **요약·키워드 추출 파이프라인**
   - LLM 프롬프트를 통해 요약(summary), 핵심 질문(key_questions), 후속 액션(action_items)을 구조화된 JSON으로 생성.
   - 임베딩 모델(OpenAI Embeddings, Sentence Transformers 등)로 chunk별 vector를 계산해 PostgreSQL pgvector 확장에 저장.
4. **노트 연동 전략**
   - 사용자가 선택한 요약·질문을 새로운 노트로 생성하거나 기존 노트에 첨부.
   - 제목 자동 추천: 핵심 질문/키워드를 조합하여 추천 타이틀 생성.
   - 관련 해시태그 자동 추천: tf-idf + 임베딩 기반 유사도 분석으로 상위 태그 제안.
5. **검색 향상**
   - 노트 검색 시 연결된 `Insight`와 `ConversationChunk` 임베딩을 활용한 의미 기반 검색 제공.
   - 질문 단위 검색: 특정 질문 문구를 입력하면 가장 유사한 chunk와 연결 노트를 반환.
6. **UX 고려 사항**
   - 대화 타임라인 뷰에서 핵심 질문을 하이라이트.
   - 노트 상세 화면에 "연결된 대화" 패널을 제공하여 출처 확인 가능.

## 9. 향후 확장 아이디어
- 협업 기능: 노트 공유, 권한 관리, 코멘트
- 모바일 최적화 및 PWA 기능
- 생성형 AI 워크플로 자동화(예: 후속 질문 추천, 이메일 전송)
- 오프라인 모드 및 동기화 큐 관리

---

## 10. FastAPI 백엔드 구현 개요
초기 버전의 FastAPI 백엔드는 다음 모듈로 구성되어 있습니다.

- `app/main.py`: FastAPI 애플리케이션 엔트리포인트 및 라우터 등록
- `app/core`: 환경 설정(`pydantic.BaseSettings`)과 보안(JWT, bcrypt) 유틸리티
- `app/db`: SQLModel 기반 데이터베이스 세션 및 초기화 로직
- `app/models`: 사용자, 노트, 태그, 대화 스레드/청크, 인사이트 테이블 정의
- `app/api`: 인증, 노트/태그, 대화 인사이트, 시스템 헬스체크 라우터
- `app/schemas`: 요청/응답 Pydantic 모델

엔드포인트는 `/api` 프리픽스 아래에 노출되며 OAuth2 password flow를 통해 발급한 JWT 토큰으로 보호됩니다.

### 환경 변수
- `DATABASE_URL`: PostgreSQL 18 (예: `postgresql+psycopg://user:pass@localhost:5432/notes`)
- `SECRET_KEY`: JWT 서명 키
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 토큰 만료 시간(분 단위)

`.env` 파일을 사용하거나 환경 변수로 주입할 수 있습니다.

### 로컬 실행 방법
```bash
# 의존성 설치 (uv 또는 pip 사용)
uv pip install -e .[dev]  # uv 사용 시
# 또는
pip install -e .[dev]

# 개발 서버 실행
uvicorn app.main:app --reload
```

### 기본 동작 확인
1. `POST /api/auth/register`로 사용자 생성
2. `POST /api/auth/login`으로 액세스 토큰 발급
3. `Authorization: Bearer <token>` 헤더로 노트/태그/대화 API 호출
4. `POST /api/conversations/import`로 생성형 AI 대화 업로드 및 청크 저장
5. `POST /api/conversations/notes/{note_id}/insights`로 대화 인사이트를 노트와 연결

### 테스트 실행
```bash
pytest
```

테스트는 SQLite 임시 데이터베이스로 실행되며 사용자 등록, 노트 CRUD, 대화 인사이트 흐름을 검증합니다.

### 수동 검증 절차
필요한 환경 변수를 설정하고 개발 서버를 실행한 뒤 아래와 같이 REST 호출을 순차적으로 수행하면 전체 플로우를 확인할 수 있습니다.

```bash
export DATABASE_URL="postgresql+psycopg://<USER>:<PASSWORD>@localhost:5432/notes"
export SECRET_KEY="dev-secret"
export ACCESS_TOKEN_EXPIRE_MINUTES="60"

uvicorn app.main:app --reload
```

별도의 터미널에서 다음 명령을 실행합니다.

1. **회원 가입**
   ```bash
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "demo@example.com", "password": "P@ssw0rd", "full_name": "데모"}'
   ```
2. **로그인 및 토큰 획득**
   ```bash
   TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d 'username=demo%40example.com&password=P%40ssw0rd' | jq -r '.access_token')
   ```
3. **노트 생성**
   ```bash
   curl -X POST http://localhost:8000/api/notes \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"title": "생성형 AI 회의록", "content": "핵심 요약", "tags": ["ai", "meeting"]}'
   ```
4. **AI 대화 업로드**
   ```bash
   curl -X POST http://localhost:8000/api/conversations/import \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"source": "chatgpt", "chunks": [{"role": "user", "content": "하나의 문장 안에 여러 질문이 있어요"}, {"role": "assistant", "content": "질문을 분리하고 요약해 드릴게요"}]}'
   ```
5. **인사이트를 노트에 연결**
   ```bash
   curl -X POST http://localhost:8000/api/conversations/notes/1/insights \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"thread_id": 1, "summary": "대화 요약", "key_questions": ["핵심 질문"], "action_items": ["후속 조치"]}'
   ```
6. **노트 검색**
   ```bash
   curl -X GET 'http://localhost:8000/api/notes?tags=ai&search=핵심' \
     -H "Authorization: Bearer ${TOKEN}"
   ```

응답에 생성한 노트와 연결된 인사이트가 포함되면 백엔드 동작을 정상적으로 확인한 것입니다.
