#!/usr/bin/env python3
"""양 OS에 최근 리뷰 100개씩 응답 생성 및 게시"""

import logging
import time
from config import Config
from models.review import Review
from services.review_bot import ReviewBot
from services.google_play_client import GooglePlayConsoleClient
from services.app_store_client import AppStoreConnectClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BATCH_LIMIT = 100


def filter_positive_reviews(reviews: list[Review]) -> list[Review]:
    """4~5점 리뷰만 필터링"""
    return [r for r in reviews if r.rating >= Config.MIN_RATING]


def run_google_play(bot: ReviewBot) -> None:
    """Google Play 최근 100개 리뷰 응답 생성 및 게시"""
    print("\n" + "=" * 50)
    print("Google Play - 최근 미답변 리뷰 100개 처리")
    print("=" * 50)

    try:
        gp_client = GooglePlayConsoleClient()
        reviews = gp_client.get_reviews(
            "KOR", limit=BATCH_LIMIT, skip_replied=True,
            infer_country_from_text=True, translation_language=None,
        )

        if not reviews:
            print("가져온 리뷰가 없습니다.")
            return

        reviews = filter_positive_reviews(reviews)
        if not reviews:
            print("4~5점 리뷰가 없습니다.")
            return

        print(f"{len(reviews)}개 긍정 리뷰 처리 시작")
        responses = bot.process_reviews_batch(reviews)

        print(f"\n응답 생성 완료: {len(responses)}개")
        print("게시 시작...")

        success = 0
        for review, response in zip(reviews, responses):
            try:
                if gp_client.post_review_response(review.id, response.response_text, "KOR"):
                    success += 1
                    print(f"[{success}] {review.id} 게시 성공")
                else:
                    print(f"[X] {review.id} 게시 실패")
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"{review.id} 게시 오류: {e}")

        print(f"\nGoogle Play 완료: {success}/{len(responses)}개 게시")

    except Exception as e:
        logger.error(f"Google Play 처리 오류: {e}")


def run_app_store(bot: ReviewBot) -> None:
    """App Store 최근 100개 리뷰 응답 생성 및 게시"""
    print("\n" + "=" * 50)
    print("App Store - 최근 미답변 리뷰 100개 처리")
    print("=" * 50)

    try:
        as_client = AppStoreConnectClient()
        reviews = as_client.get_reviews("KOR", limit=BATCH_LIMIT)

        if not reviews:
            print("가져온 리뷰가 없습니다.")
            return

        reviews = filter_positive_reviews(reviews)
        if not reviews:
            print("4~5점 리뷰가 없습니다.")
            return

        print(f"{len(reviews)}개 긍정 리뷰 처리 시작")
        responses = bot.process_reviews_batch(reviews)

        print(f"\n응답 생성 완료: {len(responses)}개")
        print("게시 시작...")

        success = 0
        for review, response in zip(reviews, responses):
            try:
                if as_client.post_review_response(review.id, response.response_text):
                    success += 1
                    print(f"[{success}] {review.id} 게시 성공")
                else:
                    print(f"[X] {review.id} 게시 실패")
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"{review.id} 게시 오류: {e}")

        print(f"\nApp Store 완료: {success}/{len(responses)}개 게시")

    except Exception as e:
        logger.error(f"App Store 처리 오류: {e}")


def main() -> None:
    """메인 실행"""
    print("내친소 리뷰봇 - 양 OS 100개씩 일괄 처리")
    bot = ReviewBot()

    run_google_play(bot)
    run_app_store(bot)

    print("\n" + "=" * 50)
    print("전체 작업 완료")
    print("=" * 50)


if __name__ == "__main__":
    main()
