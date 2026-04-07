# 내친소 리뷰봇 - 개발자 설정 가이드

## 개요
4~5점 긍정 리뷰에 자동으로 감사 응답을 생성하는 봇입니다.
Google Play + App Store 모두 지원합니다.

---

## 1. 환경 설정

```bash
# 가상환경 활성화 및 패키지 설치
source venv/bin/activate
pip install -r requirements.txt

# .env 파일 생성
cp .env.example .env
# .env 안에 실제 값 입력
```

---

## 2. 필요한 키/파일

### OpenAI API 키 (이미 설정됨)
- `.env`의 `OPENAI_API_KEY`

### App Store Connect (이미 설정됨)
- `.p8` 키 파일 → 프로젝트 폴더에 위치
- `.env`의 `APP_STORE_KEY_ID`, `APP_STORE_ISSUER_ID` 설정 완료

### ⚠️ 확인 필요: iOS Bundle ID
- 현재 `.env`에 `APP_STORE_BUNDLE_ID_KOR`이 임시값입니다
- App Store Connect → 앱 선택 → 앱 정보 → **번들 ID** 확인 후 `.env`에 입력

---

## 3. Google Play 서비스 계정 키 발급 (필요)

### Step 1: Google Cloud에서 서비스 계정 생성
1. https://console.cloud.google.com/ 접속
2. 프로젝트 선택 (없으면 새로 생성)
3. **IAM 및 관리자** → **서비스 계정** → **서비스 계정 만들기**
4. 이름: `play-review-bot` → 만들기 → 완료

### Step 2: JSON 키 다운로드
1. 생성된 서비스 계정 클릭
2. **키** 탭 → **키 추가** → **새 키 만들기** → **JSON** 선택
3. 다운로드된 `.json` 파일을 프로젝트 폴더에 넣기

### Step 3: Google Play Console에서 권한 부여
1. https://play.google.com/console/ 접속
2. **설정** → **API 액세스**
3. 위에서 만든 Google Cloud 프로젝트 연결
4. 서비스 계정 → **액세스 권한 관리** → 권한 부여:
   - ✅ 앱 정보 보기 (리뷰 읽기)
   - ✅ 리뷰에 답변 (응답 게시)
5. 앱: **내친소** 지정 → 저장

### Step 4: .env에 파일명 입력
```
GOOGLE_PLAY_SERVICE_ACCOUNT_KEY=다운받은파일명.json
```

---

## 4. 실행

```bash
source venv/bin/activate
python main.py
```

메뉴:
1. 샘플 리뷰 테스트 (API 키만 있으면 바로 가능)
2. Google Play 실제 리뷰 처리
3. 통계 조회
4. 캐시 초기화
