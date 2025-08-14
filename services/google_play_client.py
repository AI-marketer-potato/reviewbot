import json
import os
from typing import List, Dict, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from config import Config
from models.review import Review
from utils.lang_utils import detect_country_by_text

class GooglePlayConsoleClient:
    """Google Play Console API 클라이언트"""
    
    def __init__(self):
        self.service_account_file = Config.GOOGLE_PLAY_CONSOLE["SERVICE_ACCOUNT_KEY"]
        self.package_names = Config.GOOGLE_PLAY_CONSOLE["PACKAGE_NAME"]
        
        # 인증 설정
        self._setup_credentials()
        
        # Google Play Developer API 서비스 빌드
        self.service = build('androidpublisher', 'v3', credentials=self.credentials)
        
        # 유효성 검사
        self._validate_setup()
    
    def _setup_credentials(self):
        """서비스 계정 인증 설정"""
        if not os.path.exists(self.service_account_file):
            raise FileNotFoundError(f"서비스 계정 키 파일을 찾을 수 없습니다: {self.service_account_file}")
        
        # 필요한 OAuth 2.0 스코프
        scopes = ['https://www.googleapis.com/auth/androidpublisher']
        
        # 서비스 계정 인증
        self.credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file, 
            scopes=scopes
        )
    
    def _validate_setup(self):
        """설정 유효성 검사"""
        if not self.package_names:
            raise ValueError("패키지명이 설정되지 않았습니다.")
        
        # 초기화 시에는 권한 검사를 건너뛰고, test_connection에서 확인
        print("⚠️  초기화 완료. test_connection()으로 권한을 확인하세요.")
    
    def _has_developer_reply(self, review_data: Dict) -> bool:
        comments = review_data.get('comments', [])
        for comment in comments:
            if comment.get('developerComment'):
                return True
        return False
    
    def get_reviews(self, country: str, limit: int = 200, skip_replied: bool = True,
                    infer_country_from_text: bool = True,
                    translation_language: Optional[str] = None) -> List[Review]:
        """앱 리뷰 조회
        - skip_replied: 개발자 답변이 이미 달린 리뷰를 제외
        - infer_country_from_text: Google 번역으로 인해 언어가 한국어로 보이는 경우 텍스트로 국가 추정
        - translation_language: API의 translationLanguage 파라미터 전달 (예: 'ja', 'ko', 'en')
        """
        package_name = self.package_names.get(country)
        if not package_name:
            raise ValueError(f"지원하지 않는 국가 코드: {country}")
        
        try:
            # 페이지네이션을 통해 정확히 limit 개수만큼 모을 때까지 조회
            # 최근 6개월간 리뷰를 충분히 가져오기 위해 더 많은 페이지 조회
            collected: List[Review] = []
            token: Optional[str] = None
            page_size = 200  # 최대치로 설정하여 필터링 손실 보완
            max_pages = 50   # 최대 50페이지까지 조회 (약 10,000개 리뷰)
            
            total_fetched = 0
            replied_skipped = 0
            language_filtered = 0
            pages_fetched = 0
            
            while len(collected) < limit and pages_fetched < max_pages:
                request = self.service.reviews().list(
                    packageName=package_name,
                    maxResults=page_size,
                    translationLanguage=translation_language,
                    token=token
                )
                result = request.execute()
                pages_fetched += 1
                
                raw_reviews = result.get('reviews', [])
                if not raw_reviews:
                    break
                
                for review_data in raw_reviews:
                    total_fetched += 1
                    
                    if skip_replied and self._has_developer_reply(review_data):
                        replied_skipped += 1
                        continue
                    
                    review_info = review_data.get('comments', [{}])[-1]
                    user_comment = review_info.get('userComment', {})
                    
                    reviewer_lang = user_comment.get('reviewerLanguage')
                    
                                        # 텍스트 기반 국가 추정 (옵션)
                    detected_country = None
                    if infer_country_from_text:
                        detected_country = detect_country_by_text(user_comment.get('text', ''), default=country)
                    
                    # reviewerLanguage를 우선 고려해서 국가 추정 보정
                    if infer_country_from_text and reviewer_lang:
                        lang_lower = reviewer_lang.lower()
                    if lang_lower.startswith('ja'):
                        detected_country = 'JPN'
                    elif lang_lower.startswith('ko'):
                        detected_country = 'KOR'
                    elif lang_lower.startswith('en'):
                        detected_country = 'USA'
                
                effective_country = detected_country or country
                # 선택한 국가에 맞는 언어의 리뷰만 필터링
                if country == "USA" and not (effective_country == "USA" or (reviewer_lang and reviewer_lang.lower().startswith('en'))):
                    language_filtered += 1
                    continue
                elif country == "KOR" and not (effective_country == "KOR" or (reviewer_lang and reviewer_lang.lower().startswith('ko'))):
                    language_filtered += 1
                    continue
                elif country == "JPN" and not (effective_country == "JPN" or (reviewer_lang and reviewer_lang.lower().startswith('ja'))):
                    language_filtered += 1
                    continue
                    
                    review = Review(
                        id=review_data.get('reviewId'),
                        author=review_data.get('authorName', '익명'),
                        rating=user_comment.get('starRating', 0),
                        content=user_comment.get('text', ''),
                        created_at=datetime.fromtimestamp(
                            int(user_comment.get('lastModified', {}).get('seconds', 0))
                        ) if user_comment.get('lastModified') else datetime.now(),
                        country=effective_country,
                        platform="google_play",
                        language=reviewer_lang
                    )
                    collected.append(review)
                    
                    if len(collected) >= limit:
                        break
                
                # 다음 페이지 토큰
                token = None
                token_pagination = result.get('tokenPagination', {})
                if isinstance(token_pagination, dict):
                    token = token_pagination.get('nextPageToken')
                
                if not token:
                    break
            
            # 디버깅 정보 출력
            print(f"📊 Google Play 리뷰 수집 통계:")
            print(f"   - 조회한 페이지: {pages_fetched}개")
            print(f"   - 전체 조회된 리뷰: {total_fetched}개")
            print(f"   - 답변 있어서 제외: {replied_skipped}개")
            print(f"   - 언어/국가 필터로 제외: {language_filtered}개")
            print(f"   - 최종 수집된 리뷰: {len(collected)}개")
            
            # API 기본 순서를 유지하여 반환 (요청한 개수만큼 슬라이스)
            return collected[:limit]
            
        except HttpError as e:
            print(f"Google Play 리뷰 조회 오류: {e}")
            return []
        except Exception as e:
            print(f"리뷰 파싱 오류: {e}")
            return []
    
    def post_review_response(self, review_id: str, response_text: str, country: str) -> bool:
        """리뷰에 응답 게시"""
        package_name = self.package_names.get(country)
        if not package_name:
            raise ValueError(f"지원하지 않는 국가 코드: {country}")
        
        try:
            # 응답 데이터 구성
            response_body = {
                'replyText': response_text
            }
            
            # Google Play Console API로 응답 게시
            result = self.service.reviews().reply(
                packageName=package_name,
                reviewId=review_id,
                body=response_body
            ).execute()
            
            print(f"✅ Google Play 리뷰 응답 게시 성공: {review_id}")
            return True
            
        except HttpError as e:
            print(f"Google Play 리뷰 응답 게시 오류: {e}")
            return False
        except Exception as e:
            print(f"응답 게시 중 오류: {e}")
            return False
    
    def get_existing_responses(self, country: str) -> List[Dict]:
        """기존 응답 조회"""
        package_name = self.package_names.get(country)
        if not package_name:
            raise ValueError(f"지원하지 않는 국가 코드: {country}")
        
        try:
            result = self.service.reviews().list(
                packageName=package_name,
                maxResults=200
            ).execute()
            
            responses = []
            for review_data in result.get('reviews', []):
                # 개발자 응답이 있는 리뷰만 필터링
                comments = review_data.get('comments', [])
                
                for comment in comments:
                    if comment.get('developerComment'):
                        responses.append({
                            'review_id': review_data.get('reviewId'),
                            'response_text': comment['developerComment'].get('text', ''),
                            'response_date': comment['developerComment'].get('lastModified', {})
                        })
            
            return responses
            
        except Exception as e:
            print(f"기존 응답 조회 오류: {e}")
            return []
    
    def test_connection(self) -> bool:
        """API 연결 테스트"""
        try:
            # 첫 번째 패키지로 간단한 조회 테스트
            package_name = list(self.package_names.values())[0]
            
            # 리뷰 목록 조회 (1개만)
            result = self.service.reviews().list(
                packageName=package_name,
                maxResults=1
            ).execute()
            
            print("✅ Google Play Console API 연결 성공")
            print(f"패키지명: {package_name}")
            print(f"리뷰 개수: {len(result.get('reviews', []))}")
            return True
            
        except HttpError as e:
            print(f"❌ Google Play Console API 연결 실패: {e}")
            if e.resp.status == 401:
                print("인증 오류: 서비스 계정 키를 확인하세요.")
            elif e.resp.status == 403:
                print("권한 오류: Play Console에서 서비스 계정 권한을 확인하세요.")
            return False
        except Exception as e:
            print(f"❌ API 연결 테스트 중 오류: {e}")
            return False