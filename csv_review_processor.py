#!/usr/bin/env python3
"""
CSV 기반 Google Play 리뷰 응답 처리기
CSV 파일에서 리뷰를 읽어와 응답 생성 후 API로 등록
"""

import pandas as pd
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from models.review import Review, ReviewResponse
from services.review_bot import ReviewBot
from services.google_play_client import GooglePlayConsoleClient
from config import Config


class CSVReviewProcessor:
    """CSV 기반 리뷰 처리 클래스"""
    
    def __init__(self):
        self.bot = ReviewBot()
        self.gp_client = GooglePlayConsoleClient()
        self.daily_post_count = 0
        self.daily_limit = 2000  # Google Play API 일일 POST 제한
        self.processed_today = []
        
    def load_csv_reviews(self, csv_path: str) -> List[Review]:
        """CSV 파일에서 리뷰 로드"""
        try:
            # 경로에서 따옴표 제거
            csv_path = csv_path.strip().strip("'").strip('"')
            
            # Google Play Console CSV는 UTF-16 인코딩 사용
            try:
                df = pd.read_csv(csv_path, encoding='utf-16')
            except UnicodeError:
                # UTF-16 실패 시 다른 인코딩 시도
                encodings = ['utf-8', 'cp1252', 'iso-8859-1']
                df = None
                for encoding in encodings:
                    try:
                        df = pd.read_csv(csv_path, encoding=encoding)
                        break
                    except:
                        continue
                if df is None:
                    raise Exception("지원되는 인코딩을 찾을 수 없습니다.")
            
            print(f"📁 CSV 파일 로드: {len(df)}개 전체 평가 (별점 + 텍스트)")
            
            # 텍스트가 있는 리뷰만 계산
            has_text_count = (df['Review Text'].notna() & (df['Review Text'].astype(str).str.strip() != '')).sum()
            star_only_count = len(df) - has_text_count
            
            print(f"📊 평가 구분:")
            print(f"   ⭐ 별점만: {star_only_count}개 (답변 불가)")
            print(f"   📝 텍스트 포함: {has_text_count}개 (답변 가능)")
            
            # Google Play Console 실제 컬럼 확인
            required_columns = ['Star Rating', 'Review Text', 'Review Link']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"❌ 필수 컬럼 누락: {missing_columns}")
                print(f"📋 현재 컬럼: {list(df.columns)}")
                return []
            
            reviews = []
            skipped_count = 0
            no_text_count = 0
            for _, row in df.iterrows():
                # 리뷰 텍스트가 없는 경우 건너뛰기 (별점만 있는 리뷰)
                if pd.isna(row['Review Text']) or not str(row['Review Text']).strip():
                    no_text_count += 1
                    continue
                    
                # 이미 답변이 있는 리뷰는 건너뛰기
                if pd.notna(row.get('Developer Reply Text', '')) and str(row.get('Developer Reply Text', '')).strip():
                    skipped_count += 1
                    continue
                
                # Review ID는 Review Link에서 추출
                review_link = str(row['Review Link'])
                review_id = self._extract_review_id_from_link(review_link)
                
                # 리뷰 텍스트
                review_text = str(row['Review Text']).strip()
                
                # 국가/언어 추정
                country = self._detect_country_from_text(review_text, row)
                
                review = Review(
                    id=review_id,
                    author='익명',  # Google Play Console CSV에는 리뷰어명이 없음
                    rating=int(row['Star Rating']) if pd.notna(row['Star Rating']) else 5,
                    content=review_text,
                    created_at=self._parse_date(row.get('Review Submit Date and Time', '')),
                    country=country,
                    platform="google_play",
                    language=self._detect_language_from_text(review_text)
                )
                reviews.append(review)
            
            print(f"\n📋 처리 결과:")
            print(f"   📝 텍스트 있는 리뷰: {no_text_count + len(reviews) + skipped_count}개")
            print(f"   💬 이미 답변된 리뷰: {skipped_count}개")
            print(f"   🎯 미답변 리뷰: {len(reviews)}개")
            print(f"   ⭐ 별점만 있는 리뷰: {no_text_count}개 (제외)")
            print(f"\n✅ 처리 대상: {len(reviews)}개 미답변 리뷰")
            return reviews
            
        except Exception as e:
            print(f"❌ CSV 로드 실패: {e}")
            return []
    
    def _extract_review_id_from_link(self, review_link: str) -> str:
        """Review Link에서 Review ID 추출"""
        try:
            # URL 예시: http://play.google.com/console/developers/.../reviewId=36aaf342-39f6-41bc-9a6f-8e7c22aa5a26&...
            if 'reviewId=' in review_link:
                review_id = review_link.split('reviewId=')[1].split('&')[0]
                return review_id
            else:
                # reviewId가 없으면 링크 자체를 ID로 사용 (최후 수단)
                return review_link.split('/')[-1] if '/' in review_link else review_link
        except Exception:
            # 추출 실패 시 링크 자체를 ID로 사용
            return review_link
    
    def _detect_country_from_text(self, text: str, row: pd.Series) -> str:
        """텍스트 기반 국가 추정"""
        # Reviewer Language 컬럼이 있다면 활용
        if 'Reviewer Language' in row.index and pd.notna(row['Reviewer Language']):
            lang = str(row['Reviewer Language']).lower()
            if lang.startswith('ko'):
                return 'KOR'
            elif lang.startswith('ja'):
                return 'JPN'
            elif lang.startswith('en'):
                return 'USA'
        
        # 텍스트 기반 추정
        korean_chars = len([c for c in text if '\uac00' <= c <= '\ud7af'])
        japanese_chars = len([c for c in text if '\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff'])
        
        if korean_chars > japanese_chars and korean_chars > 0:
            return 'KOR'
        elif japanese_chars > 0:
            return 'JPN'
        else:
            return 'USA'
    
    def _detect_language_from_text(self, text: str) -> str:
        """텍스트 기반 언어 추정"""
        korean_chars = len([c for c in text if '\uac00' <= c <= '\ud7af'])
        japanese_chars = len([c for c in text if '\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff'])
        
        if korean_chars > japanese_chars and korean_chars > 0:
            return 'ko'
        elif japanese_chars > 0:
            return 'ja'
        else:
            return 'en'
    
    def _parse_date(self, date_str: str) -> datetime:
        """날짜 문자열 파싱"""
        if not date_str or pd.isna(date_str):
            return datetime.now()
        
        try:
            # 다양한 날짜 형식 시도
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%m/%d/%Y %H:%M:%S',
                '%m/%d/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(str(date_str), fmt)
                except ValueError:
                    continue
                    
            # 파싱 실패 시 현재 시간
            return datetime.now()
            
        except Exception:
            return datetime.now()
    
    def check_daily_quota(self) -> Dict:
        """일일 쿼터 확인"""
        today = datetime.now().strftime('%Y-%m-%d')
        quota_file = f"quota_tracker_{today}.json"
        
        try:
            if Path(quota_file).exists():
                with open(quota_file, 'r') as f:
                    data = json.load(f)
                    self.daily_post_count = data.get('post_count', 0)
                    self.processed_today = data.get('processed_reviews', [])
            else:
                self.daily_post_count = 0
                self.processed_today = []
        except Exception:
            self.daily_post_count = 0
            self.processed_today = []
        
        remaining = self.daily_limit - self.daily_post_count
        return {
            'used': self.daily_post_count,
            'remaining': remaining,
            'limit': self.daily_limit,
            'percentage': (self.daily_post_count / self.daily_limit) * 100
        }
    
    def update_quota_tracker(self, review_id: str):
        """쿼터 트래커 업데이트"""
        self.daily_post_count += 1
        self.processed_today.append(review_id)
        
        today = datetime.now().strftime('%Y-%m-%d')
        quota_file = f"quota_tracker_{today}.json"
        
        data = {
            'date': today,
            'post_count': self.daily_post_count,
            'processed_reviews': self.processed_today,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(quota_file, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 쿼터 트래커 업데이트 실패: {e}")
    
    def process_csv_reviews(self, csv_path: str, batch_size: int = 50, sample_count: int = None) -> Dict:
        """CSV 리뷰 일괄 처리"""
        print(f"\n🔄 CSV 리뷰 처리 시작: {csv_path}")
        
        # 지식베이스 초기화
        print("📚 지식베이스 초기화 중...")
        self.bot.initialize_knowledge_base(force_update=False)
        
        # 쿼터 확인
        quota_info = self.check_daily_quota()
        print(f"📊 일일 POST 쿼터: {quota_info['used']}/{quota_info['limit']} ({quota_info['percentage']:.1f}%)")
        
        if quota_info['remaining'] <= 0:
            print("❌ 일일 POST 쿼터 초과! 내일 다시 시도하세요.")
            return {'success': False, 'reason': 'quota_exceeded'}
        
        # CSV 로드
        reviews = self.load_csv_reviews(csv_path)
        if not reviews:
            return {'success': False, 'reason': 'no_reviews'}
        
        # 이미 처리된 리뷰 제외
        unprocessed_reviews = [r for r in reviews if r.id not in self.processed_today]
        if not unprocessed_reviews:
            print("✅ 모든 리뷰가 이미 처리되었습니다.")
            return {'success': True, 'processed': 0, 'skipped': len(reviews)}
        
        # 샘플 모드인 경우 개수 제한
        if sample_count and sample_count > 0:
            unprocessed_reviews = unprocessed_reviews[:sample_count]
            print(f"🧪 샘플 모드: {len(unprocessed_reviews)}개 리뷰만 처리")
        else:
            print(f"🎯 처리 대상: {len(unprocessed_reviews)}개 리뷰")
        
        # 쿼터 제한 적용
        available_quota = quota_info['remaining']
        process_count = min(len(unprocessed_reviews), available_quota)
        
        if process_count < len(unprocessed_reviews):
            print(f"⚠️ 쿼터 제한으로 {process_count}개만 처리합니다.")
        
        success_count = 0
        failed_count = 0
        
        # 배치 처리
        for i in range(0, process_count, batch_size):
            batch = unprocessed_reviews[i:i+batch_size]
            batch_index = i // batch_size + 1
            
            print(f"\n📦 배치 {batch_index} 처리 중... ({len(batch)}개)")
            
            # 1) 생성 단계: 응답 생성만 수행하고 모아두기
            batch_responses = []
            for review in batch:
                try:
                    print(f"🤖 응답 생성 중: {review.id}")
                    category = self.bot.review_classifier.classify_review(review)
                    response = self.bot.response_generator.generate_response(review, category)
                    if response is None:
                        print(f"⚠️ 비꼬는 리뷰 스킵: {review.id}")
                        continue
                    batch_responses.append({
                        'review_id': review.id,
                        'category': category,
                        'response_text': response.response_text
                    })
                    # 생성 단계에서는 잠시 대기 (과도한 LLM 호출 방지)
                    time.sleep(0.2)
                except Exception as e:
                    print(f"❌ 생성 오류 ({review.id}): {e}")
                    failed_count += 1
            
            # 배치 CSV로 저장
            try:
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                out_dir = Path('outputs')
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / f"responses_{ts}_batch{batch_index}.csv"
                pd.DataFrame(batch_responses).to_csv(out_path, index=False, encoding='utf-8-sig')
                print(f"📝 배치 {batch_index} 응답 CSV 저장: {out_path}")
            except Exception as e:
                print(f"⚠️ 배치 CSV 저장 실패: {e}")
            
            # 2) 게시 단계: 생성된 응답을 실제 API로 게시
            for item in batch_responses:
                try:
                    success = self.post_review_response(item['review_id'], item['response_text'])
                    if success:
                        print(f"✅ 게시 성공: {item['review_id']}")
                        self.update_quota_tracker(item['review_id'])
                        success_count += 1
                    else:
                        print(f"❌ 게시 실패: {item['review_id']}")
                        failed_count += 1
                    
                    # API 제한 고려하여 잠시 대기
                    time.sleep(0.5)
                    
                    # 배치 중간에도 쿼터 초과 시 중단
                    if self.daily_post_count >= self.daily_limit:
                        print("⛔ 일일 쿼터 한도 도달. 작업을 중단합니다.")
                        break
                except Exception as e:
                    print(f"❌ 게시 오류 ({item['review_id']}): {e}")
                    failed_count += 1
            
            # 쿼터 검사 후 다음 배치 진행 여부 결정
            remaining_after_batch = self.daily_limit - self.daily_post_count
            if remaining_after_batch <= 0:
                print("⛔ 일일 쿼터 한도 도달. 더 이상 배치를 진행하지 않습니다.")
                break
            
            # 배치 간 대기
            if i + batch_size < process_count:
                print("⏱️ 다음 배치까지 대기 중...")
                time.sleep(2)
        
        # 결과 요약
        result = {
            'success': True,
            'processed': success_count,
            'failed': failed_count,
            'quota_used': self.daily_post_count,
            'quota_remaining': self.daily_limit - self.daily_post_count
        }
        
        print(f"\n🎉 처리 완료!")
        print(f"✅ 성공: {success_count}개")
        print(f"❌ 실패: {failed_count}개")
        print(f"📊 남은 쿼터: {result['quota_remaining']}/{self.daily_limit}")
        
        return result
    
    def post_review_response(self, review_id: str, response_text: str) -> bool:
        """Google Play API로 리뷰 응답 등록"""
        try:
            # Google Play API 클라이언트 사용
            package_name = Config.GOOGLE_PLAY_CONSOLE["PACKAGE_NAME"]["KOR"]
            
            request_body = {
                "replyText": response_text
            }
            
            request = self.gp_client.service.reviews().reply(
                packageName=package_name,
                reviewId=review_id,
                body=request_body
            )
            
            result = request.execute()
            return True
            
        except Exception as e:
            print(f"API 오류: {e}")
            return False


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CSV 기반 Google Play 리뷰 응답 처리")
    parser.add_argument("csv_file", help="처리할 CSV 파일 경로")
    parser.add_argument("--batch-size", type=int, default=50, help="배치 크기 (기본값: 50)")
    parser.add_argument("--sample", type=int, help="샘플 모드: 지정된 개수만 처리")
    parser.add_argument("--check-quota", action="store_true", help="쿼터만 확인하고 종료")
    
    args = parser.parse_args()
    
    processor = CSVReviewProcessor()
    
    if args.check_quota:
        quota_info = processor.check_daily_quota()
        print(f"📊 일일 POST 쿼터 현황:")
        print(f"  사용: {quota_info['used']}/{quota_info['limit']} ({quota_info['percentage']:.1f}%)")
        print(f"  남음: {quota_info['remaining']}개")
        return
    
    if not Path(args.csv_file).exists():
        print(f"❌ 파일을 찾을 수 없습니다: {args.csv_file}")
        return
    
    result = processor.process_csv_reviews(args.csv_file, args.batch_size, args.sample)
    
    if result['success']:
        print(f"\n✨ 전체 작업 완료")
    else:
        print(f"\n💥 작업 실패: {result.get('reason', 'unknown')}")


if __name__ == "__main__":
    main() 