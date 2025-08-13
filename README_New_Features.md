# 새로운 기능 가이드

## 1. 최근 1주일 미답변 리뷰 전체 처리

**기존 변경사항:**
- Google Play 리뷰 처리 시 개수 입력 불필요
- 선택한 국가의 언어에 맞는 최근 1주일 미답변 리뷰 전체 자동 처리
- 국가별 언어 필터링 자동 적용

**사용법:**
```bash
python main.py
# 8번 선택 → 국가 선택 → 자동으로 해당 국가 언어의 모든 미답변 리뷰 처리
```

## 2. CSV 기반 리뷰 처리

**기능:**
- Google Play Console에서 다운로드한 CSV 파일로 과거 리뷰 처리
- 자동 응답 생성 및 API로 실제 게시
- 일일 쿼터 관리 및 중복 처리 방지

**CSV 파일 요구사항:**
```
필수 컬럼:
- Review ID: 리뷰 고유 ID
- Reviewer Name: 작성자명
- Star Rating: 별점 (1-5)
- Review Text: 리뷰 내용

선택 컬럼:
- Developer Reply Text: 기존 답변 (있으면 스킵)
- App Language: 앱 언어 설정
- Review Submit Date and Time: 작성 날짜
```

**사용법:**

### 메인 메뉴에서:
```bash
python main.py
# 10번 선택 → CSV 파일 경로 입력
```

### 직접 실행:
```bash
# 기본 처리
python csv_review_processor.py reviews.csv

# 배치 크기 조정
python csv_review_processor.py reviews.csv --batch-size 100

# 쿼터만 확인
python csv_review_processor.py --check-quota
```

**처리 과정:**
1. CSV 파일 로드 및 검증
2. 미답변 리뷰 필터링
3. 국가/언어 자동 추정
4. 일일 쿼터 확인
5. 배치별 응답 생성 및 게시
6. 진행상황 실시간 표시

## 3. Google Play API 쿼터 추적

**기능:**
- 일일 POST 요청 제한 (2,000개) 추적
- 사용량/잔량 실시간 모니터링
- 중복 처리 방지
- 자동 쿼터 파일 관리

**쿼터 확인:**
```bash
# 메인 메뉴에서
python main.py
# 11번 선택

# 또는 직접
python csv_review_processor.py --check-quota
```

**출력 예시:**
```
📊 Google Play API 일일 쿼터 현황
==================================================
🔹 사용: 450/2000 (22.5%)
🔹 남음: 1550개
✅ 충분한 쿼터가 남아있습니다.
```

**쿼터 파일:**
- `quota_tracker_2025-01-20.json`: 일일 사용량 추적
- 자동 생성/업데이트
- 처리된 리뷰 ID 목록 포함

## 사용 시나리오

### 시나리오 1: 정기적인 최신 리뷰 처리
```bash
python main.py
# 8번 → KOR → 최근 1주일 한국어 리뷰 전체 처리
```

### 시나리오 2: 과거 밀린 리뷰 처리
```bash
# 1. Google Play Console에서 리뷰 CSV 다운로드
# 2. CSV 처리
python csv_review_processor.py downloaded_reviews.csv
```

### 시나리오 3: 대량 처리 시 쿼터 관리
```bash
# 쿼터 확인
python csv_review_processor.py --check-quota

# 남은 쿼터만큼 처리 (자동 제한)
python csv_review_processor.py large_reviews.csv

# 다음날 이어서 처리 (중복 방지)
python csv_review_processor.py large_reviews.csv
```

## 주의사항

1. **API 제한**
   - Google Play: 일일 2,000개 POST 제한
   - 시간당 200개 GET 제한

2. **CSV 처리**
   - 파일 크기: 메모리 사용량 고려
   - 필수 컬럼 누락 시 처리 불가

3. **쿼터 관리**
   - 자정에 쿼터 리셋
   - 중단 후 재실행 시 이어서 처리

4. **오류 처리**
   - 실패한 리뷰는 로그 확인 후 재처리
   - 네트워크 오류 시 배치 단위로 재시도

## 문제 해결

### CSV 로드 실패
```
❌ 필수 컬럼 누락: ['Review ID']
```
→ CSV 파일의 컬럼명 확인 및 수정

### API 오류
```
❌ API 오류: 403 Forbidden
```
→ 쿼터 초과 또는 권한 문제 확인

### 쿼터 초과
```
❌ 일일 POST 쿼터 초과!
```
→ 다음날 재시도 또는 쿼터 증량 요청 