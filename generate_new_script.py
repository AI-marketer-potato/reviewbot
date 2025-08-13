#!/usr/bin/env python3
"""
Generate new review responses using the improved prompts
"""

import pandas as pd
import csv
from datetime import datetime
from services.response_generator import ResponseGenerator
from services.vector_store import VectorStoreService
from models.review import Review
import time

def categorize_review(review_content, country):
    """Categorize review based on content"""
    content_lower = review_content.lower()
    
    if country.upper() == "KOR":
        if any(word in content_lower for word in ["광고", "영상", "로딩"]):
            return "광고_관련"
        elif any(word in content_lower for word in ["포인트", "적립", "미지급"]):
            return "포인트_관련"
        elif any(word in content_lower for word in ["렉", "멈춤", "오류", "버그", "발열"]):
            return "기능_오류"
        elif any(word in content_lower for word in ["수면", "잠자기"]):
            return "수면모드_오류"
        elif any(word in content_lower for word in ["걸음", "만보"]):
            return "걸음수_문제"
        elif any(word in content_lower for word in ["좋", "으뜸", "감사", "최고"]):
            return "칭찬"
        else:
            return "기타"
    elif country.upper() == "JPN":
        if any(word in content_lower for word in ["広告", "cm", "ポイント"]):
            return "広告関連"
        elif any(word in content_lower for word in ["歩数", "歩"]):
            return "歩数問題"
        elif any(word in content_lower for word in ["エラー", "バグ", "フリーズ"]):
            return "機能エラー"
        else:
            return "その他"
    else:  # USA
        if any(word in content_lower for word in ["ad", "advertisement", "points"]):
            return "Ad Related"
        elif any(word in content_lower for word in ["steps", "walking"]):
            return "Step Tracking"
        elif any(word in content_lower for word in ["gift card", "reward", "withdrawal"]):
            return "Rewards"
        elif any(word in content_lower for word in ["bug", "error", "crash"]):
            return "Technical Issues"
        else:
            return "Other"

def process_reviews_with_improved_prompts():
    """Process all 42 reviews with the improved prompts"""
    print("🚀 Generating new script with improved prompts...")
    
    # Initialize services
    vector_store_service = VectorStoreService()
    response_generator = ResponseGenerator(vector_store_service)
    
    # Read the original CSV
    df = pd.read_csv('/Users/gravitylabs/Desktop/review/Review.csv')
    print(f"📊 Processing {len(df)} reviews")
    
    all_results = []
    
    for idx, row in df.iterrows():
        print(f"🔄 Processing review {idx + 1}/{len(df)}...")
        
        # Determine country/language
        if row['언어'] == 'KOR':
            country = 'KOR'
        elif row['언어'] == 'JPN':
            country = 'JPN'
        else:
            country = 'USA'
        
        # Create Review object
        review = Review(
            id=row['ID'],
            content=row['원본_리뷰'],
            author="",
            rating=row['평점'] if not pd.isna(row['평점']) else 3,
            country=country,
            platform=row['플랫폼'],
            created_at=datetime.now()
        )
        
        # Categorize review
        category = categorize_review(row['원본_리뷰'], country)
        
        try:
            # Generate response using improved prompts
            response = response_generator.generate_response(review, category)
            
            # Add to results
            all_results.append({
                'ID': review.id,
                '원본_리뷰': review.content,
                '언어': country,
                '플랫폼': row['플랫폼'],
                '평점': review.rating,
                '생성된_응답': response.response_text,
                '생성_시간': response.generated_at.strftime('%Y-%m-%d %H:%M:%S'),
                '사용된_소스_수': len(response.used_sources),
                '카테고리': category
            })
            
            # Small delay to avoid rate limiting
            time.sleep(0.8)
            
        except Exception as e:
            print(f"Error processing review {review.id}: {e}")
            # Add fallback result
            all_results.append({
                'ID': review.id,
                '원본_리뷰': review.content,
                '언어': country,
                '플랫폼': row['플랫폼'],
                '평점': review.rating,
                '생성된_응답': "Error in processing - please regenerate",
                '생성_시간': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '사용된_소스_수': 0,
                '카테고리': category
            })
    
    # Save final results with pipe delimiter
    output_filename = f'/Users/gravitylabs/Desktop/review/NEW_SCRIPT_42_reviews_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ID', '원본_리뷰', '언어', '플랫폼', '평점', '생성된_응답', '생성_시간', '사용된_소스_수', '카테고리']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        
        writer.writeheader()
        for result in all_results:
            writer.writerow(result)
    
    print(f"\n🎉 New script generation completed!")
    print(f"📊 Total reviews processed: {len(all_results)}")
    print(f"💾 Results saved to: {output_filename}")
    
    # Analyze quality improvements
    analyze_improvements(all_results)
    
    return output_filename

def analyze_improvements(results):
    """Analyze the quality improvements in the new script"""
    print("\n=== 📈 Quality Analysis ===")
    
    # Korean analysis
    korean_results = [r for r in results if r['언어'] == 'KOR']
    japanese_results = [r for r in results if r['언어'] == 'JPN']
    english_results = [r for r in results if r['언어'] == 'USA']
    
    print(f"🇰🇷 Korean: {len(korean_results)} reviews")
    print(f"🇯🇵 Japanese: {len(japanese_results)} reviews")
    print(f"🇺🇸 English: {len(english_results)} reviews")
    
    # Check Korean responses for issues
    korean_issues = 0
    for result in korean_results:
        response = result['생성된_응답']
        if response.count('죄송합니다') > 1:
            korean_issues += 1
        elif any(pattern in response for pattern in ['군요', '네요', '으시네요']):
            korean_issues += 1
    
    print(f"✅ Korean responses with issues: {korean_issues}/{len(korean_results)} ({korean_issues/len(korean_results)*100:.1f}%)")
    
    # Check Japanese responses for length
    japanese_long = sum(1 for r in japanese_results if len(r['생성된_응답']) > 250)
    print(f"✅ Japanese responses over 250 chars: {japanese_long}/{len(japanese_results)} ({japanese_long/len(japanese_results)*100:.1f}%)")
    
    # Show sample responses
    print("\n=== 📝 Sample New Responses ===")
    
    # Korean sample
    if korean_results:
        sample_kr = korean_results[0]
        print(f"\n🇰🇷 Korean Sample:")
        print(f"   Original: {sample_kr['원본_리뷰'][:50]}...")
        print(f"   Response: {sample_kr['생성된_응답'][:80]}...")
    
    # Japanese sample
    if japanese_results:
        sample_jp = japanese_results[0]
        print(f"\n🇯🇵 Japanese Sample:")
        print(f"   Original: {sample_jp['원본_리뷰'][:50]}...")
        print(f"   Response: {sample_jp['생성된_응답'][:80]}...")
        print(f"   Length: {len(sample_jp['생성된_응답'])} characters")
    
    # English sample
    if english_results:
        sample_en = english_results[0]
        print(f"\n🇺🇸 English Sample:")
        print(f"   Original: {sample_en['원본_리뷰'][:50]}...")
        print(f"   Response: {sample_en['생성된_응답'][:80]}...")

if __name__ == "__main__":
    process_reviews_with_improved_prompts()