#!/usr/bin/env python3
"""
Process all 42 reviews using the improved prompt system
"""

import pandas as pd
import csv
from datetime import datetime
from services.response_generator import ResponseGenerator
from services.vector_store import VectorStoreService
from models.review import Review

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

def process_all_42_reviews():
    """Process all 42 reviews using improved prompt system"""
    
    # Initialize services
    vector_store_service = VectorStoreService()
    response_generator = ResponseGenerator(vector_store_service)
    
    # Read the original CSV
    df = pd.read_csv('/Users/gravitylabs/Desktop/review/Review.csv')
    
    results = []
    
    print(f"Processing {len(df)} reviews with improved prompt system...")
    
    for idx, row in df.iterrows():
        print(f"Processing review {idx + 1}/{len(df)}...")
        
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
            author="",  # Not provided
            rating=row['평점'] if not pd.isna(row['평점']) else 3,
            country=country,
            platform=row['플랫폼'],
            created_at=datetime.now()
        )
        
        # Categorize review
        category = categorize_review(row['원본_리뷰'], country)
        
        # Generate response using improved prompt
        response = response_generator.generate_response(review, category)
        
        # Add to results
        results.append({
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
    
    return results

def save_with_pipe_delimiter(results, filename):
    """Save results to CSV with pipe delimiter"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ID', '원본_리뷰', '언어', '플랫폼', '평점', '생성된_응답', '생성_시간', '사용된_소스_수', '카테고리']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)

if __name__ == "__main__":
    print("🚀 Starting processing of all 42 reviews with improved Korean prompt system...")
    
    # Process all reviews
    all_results = process_all_42_reviews()
    
    # Save results with pipe delimiter
    output_filename = f'/Users/gravitylabs/Desktop/review/final_42_reviews_improved_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    save_with_pipe_delimiter(all_results, output_filename)
    
    print(f"\n✅ Processing completed!")
    print(f"📊 Total reviews processed: {len(all_results)}")
    print(f"💾 Results saved to: {output_filename}")
    
    # Show sample of improved Korean results
    print("\n=== 🔍 Sample Improved Korean Results ===")
    korean_count = 0
    for result in all_results:
        if result['언어'] == 'KOR' and korean_count < 3:
            print(f"🆔 ID: {result['ID']}")
            print(f"📝 Original: {result['원본_리뷰'][:60]}...")
            print(f"💬 Response: {result['생성된_응답'][:120]}...")
            print(f"🏷️ Category: {result['카테고리']}")
            print("-" * 70)
            korean_count += 1