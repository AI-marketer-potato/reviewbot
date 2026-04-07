"""리뷰봇 메인 서비스 (4~5점 긍정 리뷰 전용)"""

import json
import hashlib
import logging
import os
from datetime import datetime
from typing import Dict, List
from models.review import Review, ReviewResponse
from services.response_generator import ResponseGenerator

logger = logging.getLogger(__name__)

CACHE_FILE = "response_cache.json"


class ReviewBot:
    """긍정 리뷰 응답 봇"""

    def __init__(self):
        self.response_generator = ResponseGenerator()
        self.response_cache = self._load_cache()

    def process_review(self, review: Review) -> ReviewResponse:
        """단일 리뷰 처리"""
        cache_key = hashlib.md5(
            f"{review.content}_{review.country}_{review.platform}".encode()
        ).hexdigest()

        if cache_key in self.response_cache:
            logger.info(f"캐시 사용: {review.id}")
            return ReviewResponse(**self.response_cache[cache_key])

        response = self.response_generator.generate_response(review)

        self.response_cache[cache_key] = response.dict()
        self._save_cache()

        return response

    def process_reviews_batch(self, reviews: List[Review]) -> List[ReviewResponse]:
        """일괄 처리"""
        responses = []
        total = len(reviews)

        for i, review in enumerate(reviews, 1):
            logger.info(f"처리 중: {i}/{total} - {review.id}")
            try:
                responses.append(self.process_review(review))
            except Exception as e:
                logger.error(f"리뷰 처리 오류 {review.id}: {e}")

        logger.info(f"총 {len(responses)}개 응답 생성 완료")
        return responses

    def get_statistics(self) -> Dict:
        """통계 조회"""
        return {"총 생성된 응답": len(self.response_cache)}

    def clear_cache(self):
        """캐시 초기화"""
        self.response_cache = {}
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        print("캐시가 초기화되었습니다.")

    def _load_cache(self) -> Dict:
        """캐시 로드"""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"캐시 로드 오류: {e}")
        return {}

    def _save_cache(self):
        """캐시 저장"""
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.response_cache, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"캐시 저장 오류: {e}")
