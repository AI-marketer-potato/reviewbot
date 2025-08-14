#!/usr/bin/env python3
"""
머니워크 리뷰 응답 자동화 시스템
LangChain 기반 RAG 아키텍처를 활용한 리뷰봇
"""

import os
import sys
from datetime import datetime
from models.review import Review
from services.review_bot import ReviewBot
from services.app_store_client import AppStoreConnectClient
from schedulers.update_scheduler import UpdateScheduler
from services.google_play_client import GooglePlayConsoleClient

def print_detailed_statistics(stats: dict):
    """상세 통계 정보를 보기 좋게 출력"""
    print("\n" + "=" * 60)
    print("📊 머니워크 리뷰봇 상세 통계")
    print("=" * 60)
    
    # 기본 통계
    print(f"\n📈 기본 통계:")
    print(f"   총 생성된 응답: {stats.get('총 생성된 응답', 0):,}개")
    
    # 국가별 분포
    country_dist = stats.get('국가별 분포', {})
    if country_dist:
        print(f"\n🌍 국가별 분포:")
        for country, count in country_dist.items():
            percentage = (count / stats.get('총 생성된 응답', 1)) * 100
            print(f"   {country}: {count:,}개 ({percentage:.1f}%)")
    
    # 플랫폼별 분포
    platform_dist = stats.get('플랫폼별 분포', {})
    if platform_dist:
        print(f"\n📱 플랫폼별 분포:")
        for platform, count in platform_dist.items():
            percentage = (count / stats.get('총 생성된 응답', 1)) * 100
            print(f"   {platform}: {count:,}개 ({percentage:.1f}%)")
    
    # 카테고리별 분포
    category_dist = stats.get('카테고리별 분포', {})
    if category_dist:
        print(f"\n📂 카테고리별 분포:")
        # 카테고리를 개수 순으로 정렬
        sorted_categories = sorted(category_dist.items(), key=lambda x: x[1], reverse=True)
        for category, count in sorted_categories:
            percentage = (count / stats.get('총 생성된 응답', 1)) * 100
            print(f"   {category}: {count:,}개 ({percentage:.1f}%)")
    
    # 일별 처리량
    daily_stats = stats.get('일별 처리량 (최근)', {})
    if daily_stats:
        print(f"\n📅 최근 일별 처리량:")
        for date, count in daily_stats.items():
            print(f"   {date}: {count:,}개")
    
    # 벡터 저장소 상태
    vector_stores = stats.get('벡터 저장소 상태', {})
    if vector_stores:
        print(f"\n🗄️  벡터 저장소 상태:")
        for store, info in vector_stores.items():
            status = "✅ 로드됨" if info.get('loaded', False) else "❌ 미로드"
            doc_count = info.get('document_count', 0)
            print(f"   {store.upper()}: {status} | 문서 수: {doc_count:,}개")
    
    # 성능 지표
    performance = stats.get('성능 지표', {})
    if performance:
        print(f"\n⚡ 성능 지표:")
        print(f"   캐시 적중률: {performance.get('cache_hit_rate', 'N/A')}")
        print(f"   평균 응답 길이: {performance.get('avg_response_length', 0):.1f}자")
        print(f"   캐시 파일 크기: {performance.get('total_cache_size', 'N/A')}")
    
    # 시스템 상태
    system_status = stats.get('시스템 상태', {})
    if system_status:
        print(f"\n🔧 시스템 상태:")
        cache_exists = "✅ 존재" if system_status.get('캐시 파일 존재', False) else "❌ 없음"
        print(f"   캐시 파일: {cache_exists}")
        print(f"   벡터 저장소 경로: {system_status.get('벡터 저장소 경로', 'N/A')}")
        
        countries = system_status.get('지원 국가', [])
        categories = system_status.get('지원 카테고리', [])
        print(f"   지원 국가: {', '.join(countries)} ({len(countries)}개)")
        print(f"   지원 카테고리: {len(categories)}개")
    
    # 마지막 업데이트
    last_updated = stats.get('마지막 업데이트', '')
    if last_updated:
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n🕒 마지막 업데이트: {formatted_time}")
        except:
            print(f"\n🕒 마지막 업데이트: {last_updated}")
    
    print("\n" + "=" * 60)

def create_sample_reviews():
    """테스트용 샘플 리뷰 생성"""
    sample_reviews = [
        Review(
            id="kr_001",
            author="김민수",
            rating=2,
            content="잠자기 버튼이 사라졌어요. 어디 있나요?",
            created_at=datetime.now(),
            country="KOR",
            platform="google_play"
        ),
        Review(
            id="kr_002", 
            author="이지영",
            rating=5,
            content="앱이 정말 좋아요! 걸으면서 포인트도 모으고 재미있네요",
            created_at=datetime.now(),
            country="KOR",
            platform="app_store"
        ),
        Review(
            id="us_001",
            author="John",
            rating=1,
            content="This app is not voiceover friendly. Hard to use for blind users.",
            created_at=datetime.now(),
            country="USA",
            platform="google_play"
        ),
        Review(
            id="kr_003",
            author="박철민",
            rating=3,
            content="광고를 봤는데 포인트가 안 들어와요. 확인해주세요.",
            created_at=datetime.now(),
            country="KOR", 
            platform="google_play"
        ),
        Review(
            id="us_002",
            author="Sarah",
            rating=4,
            content="Great app! But sometimes it crashes when I try to watch ads.",
            created_at=datetime.now(),
            country="USA",
            platform="app_store"
        )
    ]
    
    return sample_reviews

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🤖 머니워크 리뷰 응답 자동화 봇")
    print("=" * 50)
    
    # 봇 초기화
    bot = ReviewBot()
    
    # 사용자 선택 메뉴
    print("\n다음 중 선택해주세요:")
    print("1. 기존 지식베이스 사용 (빠름)")
    print("2. 지식베이스 강제 업데이트 (느림, API 비용 발생)")
    print("3. 통계 조회")
    print("4. 캐시 초기화")
    print("5. App Store Connect API 테스트")
    print("6. 실제 App Store 리뷰 가져오기 및 응답")
    print("7. 샘플 리뷰 테스트")
    print("8. 실제 Google Play 리뷰 처리 (전체 국가)")
    print("9. 두 스토어 시범 처리 (각 10개)")
    print("10. CSV 기반 리뷰 처리")
    print("11. Google Play API 쿼터 확인")
    
    choice = input("\n선택 (1-11): ").strip()
    
    if choice == "1":
        # 기존 지식베이스 사용
        bot.initialize_knowledge_base(force_update=False)
    elif choice == "2":
        # 강제 업데이트
        print("\n⚠️  경고: 새로운 문서를 크롤링하고 벡터 저장소를 재생성합니다.")
        print("   OpenAI API 비용이 발생하며 시간이 오래 걸립니다.")
        confirm = input("계속하시겠습니까? (y/N): ").strip().lower()
        if confirm == 'y':
            bot.update_knowledge_base()
        else:
            print("취소되었습니다.")
            return
    elif choice == "3":
        # 통계 조회
        stats = bot.get_statistics()
        print_detailed_statistics(stats)
        return
    elif choice == "4":
        # 캐시 초기화
        bot.clear_cache()
        return
    elif choice == "5":
        # App Store API 테스트
        test_app_store_connection()
        return
    elif choice == "6":
        # 실제 App Store 리뷰 처리
        process_real_app_store_reviews(bot)
        return
    elif choice == "7":
        # 샘플 리뷰 테스트
        process_sample_reviews(bot)
        return
    elif choice == "8":
        # 실제 Google Play 리뷰 처리
        process_real_google_play_reviews(bot)
        return
    elif choice == "9":
        # 두 스토어 시범 처리
        process_trial_both_stores(bot)
        return
    elif choice == "10":
        # CSV 기반 리뷰 처리
        from csv_review_processor import CSVReviewProcessor
        csv_file = input("CSV 파일 경로를 입력하세요: ").strip().strip("'").strip('"')
        if csv_file:
            # 샘플 모드 선택
            print("\n처리 모드를 선택하세요:")
            print("1. 샘플 처리 (10개)")
            print("2. 전체 처리")
            mode_choice = input("선택 (1-2): ").strip()
            
            processor = CSVReviewProcessor()
            sample_count = 10 if mode_choice == "1" else None
            
            result = processor.process_csv_reviews(csv_file, sample_count=sample_count)
            if result['success']:
                print(f"✅ 처리 완료: {result['processed']}개 성공, {result['failed']}개 실패")
            else:
                print(f"❌ 처리 실패: {result.get('reason', 'unknown')}")
        return
    elif choice == "11":
        # Google Play API 쿼터 확인
        check_google_play_quota()
        return
    else:
        print("잘못된 선택입니다.")
        return

def test_app_store_connection():
    """App Store Connect API 연결 테스트"""
    print("\n🔗 App Store Connect API 연결 테스트...")
    
    try:
        client = AppStoreConnectClient()
        if client.test_connection():
            print("\n✅ API 연결 성공!")
            
            # 지원 국가별 앱 정보 확인
            for country in ["KOR", "USA", "JPN"]:
                try:
                    app_id = client.get_app_id(country)
                    print(f"   {country} 앱 ID: {app_id}")
                except Exception as e:
                    print(f"   {country} 앱 ID 조회 실패: {e}")
        
    except Exception as e:
        print(f"\n❌ API 연결 실패: {e}")
        print("\n다음 사항을 확인해주세요:")
        print("1. .p8 키 파일이 올바른 위치에 있는지 확인")
        print("2. .env 파일에 APP_STORE_KEY_ID, APP_STORE_ISSUER_ID가 설정되어 있는지 확인")
        print("3. Bundle ID가 올바른지 확인")

def process_real_app_store_reviews(bot: ReviewBot):
    """실제 App Store 리뷰 처리"""
    print("\n📱 실제 App Store 리뷰 처리...")
    
    try:
        # 지식베이스 초기화
        bot.initialize_knowledge_base(force_update=False)
        
        # App Store 클라이언트 초기화
        client = AppStoreConnectClient()
        
        # 국가 선택
        print("\n국가를 선택해주세요:")
        print("1. 한국 (KOR)")
        print("2. 미국 (USA)")
        print("3. 일본 (JPN)")
        
        country_choice = input("선택 (1-3): ").strip()
        if country_choice == "1":
            country = "KOR"
        elif country_choice == "2":
            country = "USA"
        elif country_choice == "3":
            country = "JPN"
        else:
            country = "KOR"  # 기본값
        
        # 리뷰 수 입력
        try:
            review_count = int(input(f"\n가져올 리뷰 수 (기본값: 10): ").strip() or "10")
        except ValueError:
            review_count = 10
        
        print(f"\n📥 {country}에서 최근 {review_count}개 리뷰 가져오는 중...")
        
        # 실제 리뷰 가져오기
        reviews = client.get_reviews(country, limit=review_count)
        
        if not reviews:
            print("❌ 가져온 리뷰가 없습니다.")
            return
        
        print(f"✅ {len(reviews)}개 리뷰를 가져왔습니다.")
        
        # 응답 생성할지 선택
        print("\n응답을 생성하시겠습니까?")
        print("1. 응답만 생성 (게시하지 않음)")
        print("2. 응답 생성 후 실제 게시")
        
        action_choice = input("선택 (1-2): ").strip()
        
        # 응답 생성
        print(f"\n🤖 {len(reviews)}개 리뷰에 대한 응답 생성 중...")
        responses = bot.process_reviews_batch(reviews)
        
        # 결과 출력
        print("\n" + "=" * 50)
        print("📋 처리 결과")
        print("=" * 50)
        
        for i, (review, response) in enumerate(zip(reviews, responses), 1):
            print(f"\n[{i}] 리뷰 ID: {review.id}")
            print(f"📝 원본: {review.content[:100]}...")
            print(f"⭐ 평점: {review.rating}")
            print(f"🤖 응답: {response.response_text}")
            print("-" * 40)
        
        # 실제 게시
        if action_choice == "2":
            print("\n📤 실제 App Store에 응답 게시 중...")
            success_count = 0
            
            for review, response in zip(reviews, responses):
                try:
                    if client.post_review_response(review.id, response.response_text):
                        success_count += 1
                        print(f"✅ {review.id} 응답 게시 성공")
                    else:
                        print(f"❌ {review.id} 응답 게시 실패")
                except Exception as e:
                    print(f"❌ {review.id} 응답 게시 오류: {e}")
            
            print(f"\n🎉 총 {success_count}/{len(responses)}개 응답 게시 완료!")
        
    except Exception as e:
        print(f"❌ 처리 중 오류 발생: {e}")

def process_sample_reviews(bot: ReviewBot):
    """샘플 리뷰 테스트 처리"""
    # 지식베이스 초기화 (기존 코드와 동일)
    bot.initialize_knowledge_base(force_update=False)
    
    # 샘플 리뷰 처리 테스트 (실제 케이스 반영)
    print("\n📝 실제 케이스 기반 샘플 리뷰 테스트...")
    
    sample_reviews = [
        # 한국 케이스들
        Review(
            id="kr_point_001",
            content="광고보고 포인트 지급 안되는 횟수가 압도적으로 많고 5초짜리 광고라고 해놓고 대놓고 15초 이상 광고 보여줌.",
            author="김사용자",
            platform="google_play",
            country="KOR",
            rating=1,
            created_at=datetime.now()
        ),
        Review(
            id="kr_sleep_001", 
            content="수면모드로 전환버튼 눌러도 안 눌릴 때가 많고 아까 낮부터는 아예 잠자기 시작 버튼 자체가 안떠요.",
            author="이사용자",
            platform="app_store",
            country="KOR", 
            rating=2,
            created_at=datetime.now()
        ),
        Review(
            id="kr_exchange_001",
            content="현금45,000원 교환 포인트 원래 7만원대였는데 지금 8만포인트네요.",
            author="박사용자",
            platform="google_play",
            country="KOR",
            rating=3,
            created_at=datetime.now()
        ),
        Review(
            id="kr_invite_001",
            content="초대코드 입력하시면 1000포인트 줍니다",
            author="최사용자",
            platform="app_store", 
            country="KOR",
            rating=5,
            created_at=datetime.now()
        ),
        Review(
            id="kr_inquiry_001",
            content="문의했는데 답변이 없어요. 채널톡으로도 연락했는데 응답이 없습니다.",
            author="정사용자",
            platform="google_play", 
            country="KOR",
            rating=1,
            created_at=datetime.now()
        ),
        # 미국 케이스들
        Review(
            id="us_step_001",
            content="I walk more than 10,000 steps each day. The app says I have walked less than 2,000.",
            author="Mare",
            platform="google_play",
            country="USA",
            rating=2,
            created_at=datetime.now()
        ),
        Review(
            id="us_accessibility_001",
            content="I have low vision and use voiceover... it's extremely frustrating for me right now.",
            author="Hali",
            platform="app_store",
            country="USA",
            rating=1,
            created_at=datetime.now()
        ),
        Review(
            id="us_giftcard_001",
            content="I ordered a gift card and I have not received it.",
            author="ET21000",
            platform="google_play",
            country="USA",
            rating=2,
            created_at=datetime.now()
        ),
        Review(
            id="us_points_001",
            content="I used to get 500 points for steps, now only 100 after cashing out.",
            author="LaLob",
            platform="app_store",
            country="USA",
            rating=3,
            created_at=datetime.now()
        ),
        Review(
            id="us_inquiry_001",
            content="I contacted support through the app but haven't received any response. I also tried the chat but no one replied.",
            author="SarahJ",
            platform="google_play",
            country="USA",
            rating=1,
            created_at=datetime.now()
        ),
        # 일본 케이스들
        Review(
            id="jp_ad_001",
            content="広告を見てもポイントがもらえないことが多いです。5秒の広告と書いてあるのに15秒以上の広告が流れます。",
            author="田中太郎",
            platform="google_play",
            country="JPN",
            rating=2,
            created_at=datetime.now()
        ),
        Review(
            id="jp_point_001",
            content="ポイントの交換レートが前より悪くなっているように感じます。改善してほしいです。",
            author="佐藤花子",
            platform="app_store",
            country="JPN",
            rating=3,
            created_at=datetime.now()
        ),
        Review(
            id="jp_positive_001",
            content="毎日楽しく使わせていただいています！ポイントも貯まりやすくて嬉しいです。",
            author="山田次郎",
            platform="google_play",
            country="JPN",
            rating=5,
            created_at=datetime.now()
        )
    ]
    
    # 리뷰 처리
    responses = bot.process_reviews_batch(sample_reviews)
    
    # 결과 출력
    print("\n" + "=" * 50)
    print("📋 생성된 응답 결과")
    print("=" * 50)
    
    for i, response in enumerate(responses, 1):
        review = sample_reviews[i-1]  # 해당 리뷰 가져오기
        
        print(f"\n[{i}] 리뷰 ID: {response.review_id}")
        print(f"📍 국가: {response.country} | 플랫폼: {response.platform}")
        print(f"📝 원본 리뷰: {review.content}")
        print(f"🤖 생성된 응답:")
        print("-" * 40)
        print(response.response_text)
        print("-" * 40)
        print(f"📚 사용된 소스: {len(response.used_sources)}개")
        
    print(f"\n✅ 총 {len(responses)}개 응답 생성 완료!")
    
    # 벡터 저장소 정보 출력
    vector_info = bot.vector_store_service.get_store_info()
    print(f"\n📊 벡터 저장소 상태: {vector_info}")
    
    print("\n🎉 테스트 완료! 실제 운영 시에는 API를 통해 리뷰를 수집하고 응답을 게시할 수 있습니다.")

def check_google_play_quota():
    """Google Play API POST 쿼터 확인"""
    from csv_review_processor import CSVReviewProcessor
    processor = CSVReviewProcessor()
    quota_info = processor.check_daily_quota()
    
    print(f"\n📊 Google Play API 일일 쿼터 현황")
    print("=" * 50)
    print(f"🔹 사용: {quota_info['used']}/{quota_info['limit']} ({quota_info['percentage']:.1f}%)")
    print(f"🔹 남음: {quota_info['remaining']}개")
    
    if quota_info['remaining'] <= 100:
        print("⚠️ 쿼터가 부족합니다!")
    elif quota_info['remaining'] <= 500:
        print("⚠️ 쿼터 사용량에 주의하세요.")
    else:
        print("✅ 충분한 쿼터가 남아있습니다.")

def process_real_google_play_reviews(bot: ReviewBot):
    """실제 Google Play 리뷰 처리 - 모든 국가 통합"""
    print("\n📱 실제 Google Play 리뷰 처리 (전체 국가)...")
    
    try:
        from csv_review_processor import CSVReviewProcessor
        
        # 지식베이스 초기화
        bot.initialize_knowledge_base(force_update=False)
        
        # 쿼터 확인
        processor = CSVReviewProcessor()
        quota_info = processor.check_daily_quota()
        print(f"\n📊 Google Play API 쿼터: {quota_info['used']}/{quota_info['limit']} ({quota_info['percentage']:.1f}%)")
        
        if quota_info['remaining'] <= 0:
            print("❌ 일일 POST 쿼터 초과! 내일 다시 시도하세요.")
            return
        
        # Google Play 클라이언트 초기화
        gp_client = GooglePlayConsoleClient()
        
        print(f"\n📥 모든 국가 최근 1주일 미답변 리뷰 전체 가져오는 중...")
        
        # 모든 국가의 리뷰를 한 번에 가져오기
        all_reviews = []
        countries = ["KOR", "USA", "JPN"]
        
        for country in countries:
            print(f"\n🌍 {country} 리뷰 수집 중...")
            country_reviews = gp_client.get_reviews(
                country,
                limit=2000,  # 충분히 큰 수로 설정하여 전체 가져오기
                skip_replied=True,  # 답변된 리뷰는 제외
                infer_country_from_text=True,
                translation_language=None
            )
            all_reviews.extend(country_reviews)
            print(f"✅ {country}: {len(country_reviews)}개 리뷰 수집")
            
        reviews = all_reviews
        
        if not reviews:
            print("❌ 가져온 리뷰가 없습니다.")
            return
        
        print(f"\n📊 전체 수집 결과:")
        print(f"✅ 총 {len(reviews)}개 미답변 리뷰 수집 완료")
        
        # 국가별 통계
        country_stats = {}
        for review in reviews:
            country_stats[review.country] = country_stats.get(review.country, 0) + 1
        
        for country, count in country_stats.items():
            print(f"   - {country}: {count}개")
        
        # 쿼터 제한 확인
        available_quota = quota_info['remaining']
        if len(reviews) > available_quota:
            print(f"⚠️ 쿼터 제한으로 {available_quota}개만 처리 가능합니다.")
        
        # 응답 생성할지 선택
        print("\n응답을 생성하시겠습니까?")
        print("1. 응답만 생성 (게시하지 않음)")
        print("2. 응답 생성 후 실제 게시")
        
        action_choice = input("선택 (1-2): ").strip()
        
        # 응답 생성
        print(f"\n🤖 {len(reviews)}개 리뷰에 대한 응답 생성 중...")
        responses = bot.process_reviews_batch(reviews)
        
        # 결과 출력
        print("\n" + "=" * 50)
        print("📋 처리 결과")
        print("=" * 50)
        
        for i, (review, response) in enumerate(zip(reviews, responses), 1):
            print(f"\n[{i}] 리뷰 ID: {review.id}")
            print(f"📍 국가: {review.country} | 플랫폼: {review.platform}")
            print(f"📝 원본: {review.content[:100]}...")
            print(f"⭐ 평점: {review.rating}")
            print(f"🤖 응답: {response.response_text}")
            print("-" * 40)
        
        # 실제 게시
        if action_choice == "2":
            print("\n📤 실제 Google Play에 응답 게시 중...")
            success_count = 0
            remaining_quota = quota_info['remaining']
            
            for i, (review, response) in enumerate(zip(reviews, responses)):
                if i >= remaining_quota:
                    print(f"⚠️ 일일 쿼터 제한으로 {i}개만 처리됩니다.")
                    break
                    
                try:
                    # 국가별로 다른 처리 (각 리뷰의 country 속성 사용)
                    success = gp_client.post_review_response(review.id, response.response_text, review.country)
                    if success:
                        success_count += 1
                        processor.update_quota_tracker(review.id)
                        print(f"✅ {review.id} 응답 게시 성공")
                    else:
                        print(f"❌ {review.id} 응답 게시 실패")
                except Exception as e:
                    print(f"❌ {review.id} 응답 게시 오류: {e}")
            
            print(f"\n🎉 총 {success_count}/{len(responses)}개 응답 게시 완료!")
            print(f"📊 남은 쿼터: {quota_info['remaining'] - success_count}/{quota_info['limit']}")
        
    except Exception as e:
        print(f"❌ 처리 중 오류 발생: {e}")

def process_trial_both_stores(bot: ReviewBot):
    """두 스토어에서 각각 10개 시범 처리 (동일 국가 선택)"""
    print("\n🧪 두 스토어 시범 처리 (각 10개)")
    
    try:
        # 지식베이스 초기화
        bot.initialize_knowledge_base(force_update=False)
        
        # 클라이언트 초기화
        as_client = AppStoreConnectClient()
        gp_client = GooglePlayConsoleClient()
        
        # 국가 선택
        print("\n국가를 선택해주세요:")
        print("1. 한국 (KOR)")
        print("2. 미국 (USA)")
        print("3. 일본 (JPN)")
        
        country_choice = input("선택 (1-3): ").strip()
        if country_choice == "1":
            country = "KOR"
        elif country_choice == "2":
            country = "USA"
        elif country_choice == "3":
            country = "JPN"
        else:
            country = "KOR"
        
        review_count = 10
        print(f"\n📥 {country}에서 각 스토어별 최근 {review_count}개 리뷰 가져오는 중...")
        
        # 리뷰 수집
        as_reviews = []
        gp_reviews = []
        try:
            as_reviews = as_client.get_reviews(country, limit=review_count)
        except Exception as e:
            print(f"App Store 리뷰 조회 실패: {e}")
        try:
            gp_reviews = gp_client.get_reviews(country, limit=review_count, infer_country_from_text=True)
        except Exception as e:
            print(f"Google Play 리뷰 조회 실패: {e}")
        
        print(f"✅ App Store: {len(as_reviews)}개, Google Play: {len(gp_reviews)}개")
        
        # 응답 생성
        if as_reviews:
            print("\n🤖 App Store 응답 생성 중...")
            as_responses = bot.process_reviews_batch(as_reviews)
        else:
            as_responses = []
        if gp_reviews:
            print("\n🤖 Google Play 응답 생성 중...")
            gp_responses = bot.process_reviews_batch(gp_reviews)
        else:
            gp_responses = []
        
        # 결과 출력
        def print_results(store_name, reviews, responses):
            if not reviews:
                print(f"\n{store_name}: 처리할 리뷰가 없습니다.")
                return
            print("\n" + "=" * 50)
            print(f"📋 {store_name} 처리 결과")
            print("=" * 50)
            for i, (review, response) in enumerate(zip(reviews, responses), 1):
                print(f"\n[{i}] 리뷰 ID: {review.id}")
                print(f"📝 원본: {review.content[:100]}...")
                print(f"⭐ 평점: {review.rating}")
                print(f"🤖 응답: {response.response_text}")
                print("-" * 40)
        
        print_results("App Store", as_reviews, as_responses)
        print_results("Google Play", gp_reviews, gp_responses)
        
        # 게시 여부
        print("\n응답을 실제로 게시하시겠습니까?")
        print("1. 게시하지 않음 (미리보기만)")
        print("2. 두 스토어 모두 게시")
        action_choice = input("선택 (1-2): ").strip()
        
        if action_choice == "2":
            # App Store 게시
            if as_reviews and as_responses:
                print("\n📤 App Store에 응답 게시 중...")
                success_count = 0
                for review, response in zip(as_reviews, as_responses):
                    try:
                        if as_client.post_review_response(review.id, response.response_text):
                            success_count += 1
                            print(f"✅ {review.id} 응답 게시 성공")
                        else:
                            print(f"❌ {review.id} 응답 게시 실패")
                    except Exception as e:
                        print(f"❌ {review.id} 응답 게시 오류: {e}")
                print(f"🎉 App Store 게시 완료: {success_count}/{len(as_responses)}")
            
            # Google Play 게시
            if gp_reviews and gp_responses:
                print("\n📤 Google Play에 응답 게시 중...")
                success_count = 0
                for review, response in zip(gp_reviews, gp_responses):
                    try:
                        if gp_client.post_review_response(review.id, response.response_text, country):
                            success_count += 1
                            print(f"✅ {review.id} 응답 게시 성공")
                        else:
                            print(f"❌ {review.id} 응답 게시 실패")
                    except Exception as e:
                        print(f"❌ {review.id} 응답 게시 오류: {e}")
                print(f"🎉 Google Play 게시 완료: {success_count}/{len(gp_responses)}")
        
    except Exception as e:
        print(f"❌ 시범 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    main() 