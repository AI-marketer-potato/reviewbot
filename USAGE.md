# 내친소 리뷰봇 사용 설명서

App Store / Google Play 한국 스토어에 올라온 **4~5점 긍정 리뷰**에 자동으로 감사 응답을 게시하는 봇입니다.

---

## 1. 무엇을 해주는 봇인가요?

- 한국 App Store, Google Play 스토어에서 **미답변 4~5점 리뷰**를 가져옵니다.
- OpenAI(GPT-4o-mini)로 리뷰 내용에 맞는 답변을 생성합니다.
- 생성된 답변을 각 스토어에 자동으로 게시합니다.
- 짧은 리뷰("좋아요" 등)는 고정 응답, 비꼬는 리뷰는 자동 스킵합니다.
- 1~3점 리뷰는 처리 대상이 아닙니다(`config.py`의 `MIN_RATING = 4`).

---

## 2. 처음 한 번 세팅하기

### 2.1 가상환경 & 라이브러리 설치
```bash
cd /Users/daniel_0220/Desktop/about_coding/reviewbot
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### 2.2 `.env` 파일 만들기
프로젝트 루트(`reviewbot/`)에 `.env` 파일을 만들고 아래 값을 채웁니다.

```bash
# OpenAI (필수)
OPENAI_API_KEY=sk-...

# Google Play Console
GOOGLE_PLAY_PACKAGE_NAME_KOR=com.retrieverSalon.naechinso
GOOGLE_PLAY_SERVICE_ACCOUNT_KEY=service_account.json

# App Store Connect
APP_STORE_KEY_ID=...                # Apple Developer에서 발급한 Key ID
APP_STORE_ISSUER_ID=56ce57a7-9dc1-4b97-9781-c0c00963c18a
APP_STORE_PRIVATE_KEY_PATH=AuthKey_DJ9W6DK66M.p8
APP_STORE_BUNDLE_ID_KOR=com.retrieverSalon.naechinso
```

### 2.3 인증 파일 두 개 확인
- `service_account.json` — Google Play Console 서비스 계정 키
- `AuthKey_XXXXXX.p8` — App Store Connect API Key (Apple Developer 계정에서 발급)

두 파일 모두 프로젝트 루트에 있어야 합니다.

---

## 3. 사용법

### 3.1 일괄 처리 (가장 자주 쓰는 방법)
양 스토어에서 **최신 미답변 4~5점 리뷰 100개씩**을 한 번에 처리합니다.

```bash
./venv/bin/python run_batch_100.py
```

실행하면 자동으로:
1. Google Play 미답변 리뷰 가져오기 → 답변 생성 → 게시
2. App Store 미답변 리뷰 가져오기 → 답변 생성 → 게시

### 3.2 메뉴 모드 (수동 확인하면서 처리)
미리보기로 답변을 검토한 뒤 게시할지 결정하고 싶을 때 씁니다.

```bash
./venv/bin/python main.py
```

메뉴:
- `1` 샘플 리뷰 테스트 (실제 게시 안 함)
- `2` App Store 실제 리뷰 처리
- `3` Google Play 실제 리뷰 처리
- `4` 통계 조회
- `5` 캐시 초기화

`2`나 `3`을 선택하면 다시 묻습니다:
- `1` 응답만 생성 (게시 X)
- `2` 응답 생성 후 실제 게시

---

## 4. 자주 쓰는 시나리오

### A. 매일 새 리뷰에 답변하고 싶다
```bash
./venv/bin/python run_batch_100.py
```
하루에 한 번 돌리면 충분합니다 (보통 신규 리뷰 < 100개).

### B. 답변을 미리 보고 싶다
```bash
./venv/bin/python main.py
# 2 또는 3 → 1 (응답만 생성)
```

### C. 200개 넘는 오래된 미답변이 쌓여있다
`run_batch_100.py`는 한 번에 100개씩만 처리하니 여러 번 돌립니다. 그래도 못 잡는 오래된 페이지가 있다면 페이지네이션 스크립트가 별도로 필요합니다 (담당자 문의).

---

## 5. 처리 결과 확인

- 콘솔 출력: `[N] {review_id} 게시 성공` / `[X] 게시 실패`
- `review_responses.csv`: 모든 생성된 응답 기록
- `response_cache.json`: 중복 응답 방지용 캐시
- App Store Connect / Google Play Console에서 직접 확인 가능

---

## 6. 자주 만나는 문제

| 증상 | 원인/해결 |
|---|---|
| `OPENAI_API_KEY가 설정되지 않았습니다` | `.env`에 `OPENAI_API_KEY` 추가 |
| `Private key 파일을 찾을 수 없습니다` | `.p8` 파일이 프로젝트 루트에 있는지 확인. `.env`의 `APP_STORE_PRIVATE_KEY_PATH` 경로 확인 |
| `Bundle ID에 해당하는 앱을 찾을 수 없습니다` | `APP_STORE_BUNDLE_ID_KOR` 값이 App Store Connect의 실제 Bundle ID와 일치하는지 확인 |
| Google Play `403 The caller does not have permission` | `service_account.json`의 서비스 계정에 Play Console 답글 권한이 부여됐는지 확인 |
| `4~5점 리뷰가 없습니다` | 미답변 4~5점 리뷰가 진짜 없거나, 최신 100개 안에 다 답변 완료된 상태 (정상) |

---

## 7. 동작 방식 (간단히)

```
[run_batch_100.py / main.py]
        │
        ▼
[Google Play / App Store API]    ← 미답변 4~5점 리뷰 가져오기
        │
        ▼
[ReviewBot]                       ← OpenAI로 답변 생성
   - 짧은 리뷰: 고정 응답 (다양화)
   - 비꼬는 리뷰: 스킵
   - 일반 리뷰: GPT-4o-mini로 페르소나 응답
        │
        ▼
[Google Play / App Store API]     ← 응답 게시
        │
        ▼
[review_responses.csv 저장]
```

---

## 8. 주의사항

- 한 번 게시된 답변은 **공개적으로 보입니다**. 게시 전에 답변 톤이 적절한지 확인하세요.
- App Store에 같은 리뷰에 두 번 POST하면 **답변이 덮어쓰기** 됩니다 (중복 X).
- OpenAI API 호출 비용이 발생합니다 (gpt-4o-mini 기준 리뷰 100개당 약 $0.05~0.10).
- 1~3점 부정 리뷰는 자동 처리되지 않으니 수동으로 답변하세요.

---

## 9. 파일 구조

```
reviewbot/
├── main.py                 # 메뉴 모드 진입점
├── run_batch_100.py        # 일괄 처리 진입점
├── config.py               # 설정 (MIN_RATING, 모델명 등)
├── .env                    # 비밀 정보 (직접 작성)
├── service_account.json    # Google Play 인증 (직접 배치)
├── AuthKey_*.p8            # App Store 인증 (직접 배치)
├── services/
│   ├── review_bot.py       # 답변 생성 로직
│   ├── google_play_client.py
│   └── app_store_client.py
├── models/
│   └── review.py
├── review_responses.csv    # 게시 기록
└── response_cache.json     # 응답 캐시
```
