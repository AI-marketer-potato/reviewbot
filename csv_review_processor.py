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
            df = pd.read_csv(csv_path)
            print(f"📁 CSV 파일 로드: {len(df)}개 리뷰")
            
            # CSV 컬럼 확인
            required_columns = ['Review ID', 'Reviewer Name', 'Star Rating', 'Review Text']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"❌ 필수 컬럼 누락: {missing_columns}")
                print(f"📋 현재 컬럼: {list(df.columns)}")
                return []
            
            reviews = []
            for _, row in df.iterrows():
                # 이미 답변이 있는 리뷰는 건너뛰기
                if pd.notna(row.get('Developer Reply Text', '')):
                    continue
                
                # 국가/언어 추정
                review_text = str(row['Review Text'])
                country = self._detect_country_from_text(review_text, row)
                
                review = Review(
                    id=str(row['Review ID']),
                    author=str(row['Reviewer Name']) if pd.notna(row['Reviewer Name']) else '익명',
                    rating=int(row['Star Rating']) if pd.notna(row['Star Rating']) else 5,
                    content=review_text,
                    created_at=self._parse_date(row.get('Review Submit Date and Time', '')),
                    country=country,
                    platform="google_play",
                    language=self._detect_language_from_text(review_text)
                )
                reviews.append(review)
            
            print(f"✅ 미답변 리뷰 {len(reviews)}개 로드 완료")
            return reviews
            
        except Exception as e:
            print(f"❌ CSV 로드 실패: {e}")
            return []
    
    def _detect_country_from_text(self, text: str, row: pd.Series) -> str:
        """텍스트 기반 국가 추정"""
        # App Language 컬럼이 있다면 활용
        if 'App Language' in row.index and pd.notna(row['App Language']):
            lang = str(row['App Language']).lower()
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
    
    def process_csv_reviews(self, csv_path: str, batch_size: int = 50) -> Dict:
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
            
            print(f"\n📦 배치 {i//batch_size + 1} 처리 중... ({len(batch)}개)")
            
            for review in batch:
                try:
                    # 응답 생성
                    print(f"🤖 응답 생성 중: {review.id}")
                    category = self.bot.classifier.classify_review(review.content, review.country)
                    response = self.bot.response_generator.generate_response(review, category)
                    
                    # API로 응답 등록
                    success = self.post_review_response(review.id, response.response_text)
                    
                    if success:
                        print(f"✅ 성공: {review.id}")
                        self.update_quota_tracker(review.id)
                        success_count += 1
                    else:
                        print(f"❌ 실패: {review.id}")
                        failed_count += 1
                    
                    # API 제한 고려하여 잠시 대기
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"❌ 오류 ({review.id}): {e}")
                    failed_count += 1
            
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
    
    result = processor.process_csv_reviews(args.csv_file, args.batch_size)
    
    if result['success']:
        print(f"\n✨ 전체 작업 완료")
    else:
        print(f"\n💥 작업 실패: {result.get('reason', 'unknown')}")


if __name__ == "__main__":
    main() 