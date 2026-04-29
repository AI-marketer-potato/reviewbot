# ReviewBot SaaS 프로덕트화 컨텍스트

> 새 레포에서 다중 고객사(내친소, 머니워크, 향후 추가)를 지원하는 B2B SaaS로 확장하기 위한 출발점 문서.
> 이 문서는 **새 레포로 가져갈 컨텍스트**입니다. 현재 레포는 내친소 단일 고객사 PoC로 유지합니다.

---

## 1. 현재 상태 (As-is)

### 1.1 어떤 봇인가
- **단일 고객사(내친소) 전용** Python CLI 봇
- 한국 App Store + Google Play 4~5점 미답변 리뷰에 자동 응답 게시
- 실행 방식: `./venv/bin/python run_batch_100.py` (수동 실행)
- 1차 운영 결과: 약 235개 리뷰에 응답 게시 완료

### 1.2 핵심 컴포넌트
```
services/
├── review_bot.py           # OpenAI 기반 응답 생성 (페르소나 + 카테고리 분류)
├── google_play_client.py   # Google Play Console API
└── app_store_client.py     # App Store Connect API
config.py                   # 단일 .env 기반 설정 (멀티테넌트 X)
```

### 1.3 한계
- **단일 테넌트**: `.env` 하나, 인증 파일 하나, 하드코딩된 패키지명/번들 ID
- **수동 실행**: 크론/스케줄러 없음 (`schedulers/` 디렉토리는 골격만)
- **로컬 데이터**: CSV/JSON 파일에 결과 저장 (DB 없음)
- **응답 톤 커스터마이징 불가**: 코드에 페르소나가 박혀있음
- **대시보드 없음**: `web/` 폴더에 Next.js 골격만 있음 (미완성)

---

## 2. SaaS 프로덕트 비전 (To-be)

### 2.1 타겟 고객
1. **내친소** (현재 운영 중) — 데이팅 앱
2. **머니워크** — 리워드/포인트 앱 (다음 온보딩 대상)
3. 이후 한국 시장 중소~중견 앱 운영사

### 2.2 플랜 구조 (`STITCH_BRIEF.md` 기반)

| 플랜 | 대상 | 핵심 기능 |
|---|---|---|
| **Lite** | 내친소 같은 소규모 앱 | 4~5점 자동 응답, 고정 페르소나, 짧은 리뷰 고정 응답, 비꼬는 리뷰 자동 스킵, 기본 대시보드 |
| **Premium** | 머니워크 등 운영 리소스가 있는 앱 | 1~5점 전체 응답, 커스텀 페르소나/톤, 카테고리 룰 정의, 지식베이스(RAG), 사용자 정의 응답 템플릿, 고급 분석 |

### 2.3 멀티테넌트 핵심 요구사항
1. **고객사별 인증 파일 분리** (`.p8`, `service_account.json`)
2. **고객사별 페르소나/톤 설정**
3. **고객사별 패키지명/번들 ID 매핑**
4. **고객사별 사용량 추적 & 빌링**
5. **고객사별 응답 로그 격리**

---

## 3. 새 레포 아키텍처 제안

### 3.1 디렉토리 구조
```
reviewbot-saas/
├── apps/
│   ├── api/                # FastAPI 백엔드 (멀티테넌트 API)
│   ├── worker/             # 스케줄러 + 워커 (Celery / RQ / APScheduler)
│   └── web/                # Next.js 대시보드 (현재 web/ 폴더 발전형)
├── packages/
│   ├── core/               # 현 services/review_bot.py 일반화
│   ├── stores/
│   │   ├── google_play.py  # 현 google_play_client.py
│   │   └── app_store.py    # 현 app_store_client.py
│   ├── personas/           # 고객사별 페르소나/톤 정의
│   └── db/                 # SQLAlchemy/Prisma 스키마 + 마이그레이션
├── infra/
│   ├── docker-compose.yml
│   └── terraform/          # (옵션)
└── docs/
    ├── PRODUCT_CONTEXT.md  # 이 문서
    └── ONBOARDING.md       # 신규 고객사 온보딩 절차
```

### 3.2 데이터 모델 (초안)
```python
class Tenant:                       # 고객사
    id, name, plan, created_at
    google_play_package_name
    app_store_bundle_id
    app_store_app_id
    persona_config (jsonb)          # 톤, 이름, 시그니처 등
    response_rules (jsonb)          # 4점 미만 처리 정책 등

class TenantCredential:             # 인증 파일 (암호화 저장)
    tenant_id
    type (google_play_sa | app_store_jwt)
    encrypted_payload
    key_id, issuer_id (App Store만)

class Review:
    tenant_id
    platform (google_play | app_store)
    external_id, country, rating
    content, author, created_at
    fetched_at

class ReviewResponse:
    review_id, tenant_id
    response_text
    generated_at, posted_at
    status (generated | posted | failed | skipped)
    skip_reason, llm_model, llm_cost_usd

class UsageMetric:                  # 빌링용
    tenant_id, period (yyyy-mm)
    reviews_processed, responses_posted
    llm_input_tokens, llm_output_tokens
```

### 3.3 처리 흐름 (스케줄러 기반)
```
[Cron N분마다] → [각 Tenant 순회]
                  → [GP/AS API에서 미답변 리뷰 fetch]
                  → [페르소나 적용 응답 생성]
                  → [DB 저장]
                  → [GP/AS에 게시]
                  → [usage_metric 갱신]
```

---

## 4. 마이그레이션 계획

### Phase 1: 코어 추출 (현 레포 → 새 레포)
- [ ] `services/review_bot.py` → `packages/core/bot.py` (페르소나 주입식 리팩토링)
- [ ] `services/google_play_client.py` → `packages/stores/google_play.py` (자격증명을 인자로 받기)
- [ ] `services/app_store_client.py` → `packages/stores/app_store.py` (동일)
- [ ] 페르소나 로직 분리 (현재 코드에 박힌 한국어 응답 톤을 `personas/naechinso.yaml`로)

### Phase 2: 멀티테넌트 인프라
- [ ] DB 스키마 + 마이그레이션 (Postgres)
- [ ] FastAPI 백엔드 (Tenant CRUD, Credential 업로드, 수동 트리거 엔드포인트)
- [ ] 스케줄러 (Celery beat 또는 APScheduler)
- [ ] 자격증명 암호화 저장 (KMS / Fernet)

### Phase 3: 고객사 온보딩
- [ ] **내친소** 마이그레이션 (현 `.env` + 인증 파일을 새 시스템에 등록)
- [ ] **머니워크** 신규 온보딩
  - 머니워크 페르소나 정의 (포인트/광고/기능 카테고리에 맞는 톤)
  - 머니워크 Google Play 서비스 계정 + App Store API Key 수령
  - DB에 Tenant 등록 → 첫 dry-run → 게시 시작

### Phase 4: 대시보드 & 빌링
- [ ] Next.js 대시보드 (현 `web/` 발전)
  - 처리량 그래프, 응답 미리보기, 페르소나 편집 UI
- [ ] 사용량 기반 빌링 (Stripe)

---

## 5. 머니워크 추가 시 고려사항

내친소와 다른 점:
- **리뷰 카테고리가 다름**: 포인트, 광고 시청, 출금, 기능 오류 등 (현 `config.py:21`의 `REVIEW_CATEGORIES`가 이미 머니워크 시절 정의됨 — 재사용 가능)
- **페르소나 톤이 다름**: 내친소는 친근한 데이팅 톤, 머니워크는 신뢰감 있는 핀테크 톤
- **부정 리뷰 비중이 더 높을 수 있음**: 포인트/출금 이슈 → Premium 플랜 필요 (1점도 응답)
- **지식베이스 필요**: 출금 정책, 포인트 적립 룰 등 → RAG 도입

---

## 6. 새 레포 시작 시 첫 커밋에 포함할 것

1. 이 문서 (`docs/PRODUCT_CONTEXT.md`)
2. `STITCH_BRIEF.md` (디자인 브리프)
3. 현 레포의 `services/` 코드 (라이선스/저자 정보 유지)
4. 현 레포의 `models/review.py` (데이터 모델 출발점)
5. 현 레포의 `requirements.txt` (의존성 출발점)

**가져가지 말 것**:
- `.env`, `*.p8`, `service_account.json` (자격증명은 새로 발급 후 DB에 암호화 저장)
- `response_cache.json`, `review_responses.csv` (단일 테넌트 데이터)
- `venv/`, `__pycache__/`

---

## 7. 결정 필요 사항 (열린 질문)

- [ ] 새 레포 이름? (`reviewbot-saas`, `replyhub`, ...)
- [ ] 백엔드 스택: Python(FastAPI) 유지 vs Node 전환? — 현 코드 재사용 위해 Python 권장
- [ ] DB: Postgres + SQLAlchemy vs Supabase? — 빠른 MVP면 Supabase
- [ ] 호스팅: Vercel(web) + Fly.io/Railway(api+worker) vs 단일 클라우드?
- [ ] 자격증명 보관: Vault / AWS Secrets Manager / DB 암호화?
- [ ] 머니워크 대상 첫 출시일?
- [ ] LLM 모델: 현재 `gpt-4o-mini` 유지 (검증 끝, 가장 저렴)

---

## 8. 참고 (현 레포 내 관련 파일)

- `STITCH_BRIEF.md` — 디자인/플랜 브리프
- `USAGE.md` — 현 봇 사용 설명서
- `services/review_bot.py` — 응답 생성 로직 (페르소나 분리 대상)
- `services/app_store_client.py:127` — `skip_replied` 필터 (수정 완료)
- `config.py:21` — 카테고리 정의 (재사용 가능)
- `web/` — Next.js 대시보드 골격 (이전 가능)
