#!/usr/bin/env python3
"""
Process all 42 reviews with the final improved Korean prompt
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

def process_batch(df_batch, batch_num, response_generator):
    """Process a batch of reviews"""
    batch_results = []
    
    for idx, row in df_batch.iterrows():
        print(f"Batch {batch_num}: Processing review {idx + 1}...")
        
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
            # Generate response using final improved prompt
            response = response_generator.generate_response(review, category)
            
            # Add to results
            batch_results.append({
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
            batch_results.append({
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
    
    return batch_results

def save_with_pipe_delimiter(results, filename):
    """Save results to CSV with pipe delimiter"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ID', '원본_리뷰', '언어', '플랫폼', '평점', '생성된_응답', '생성_시간', '사용된_소스_수', '카테고리']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)

def analyze_korean_responses(results):
    """Analyze Korean responses for quality issues"""
    print("\n=== 🔍 Korean Response Quality Analysis ===")
    
    korean_results = [r for r in results if r['언어'] == 'KOR']
    total_korean = len(korean_results)
    
    issue_counts = {
        'apology_overuse': 0,
        'observational_tone': 0,
        'emotion_prediction': 0,
        'missing_greeting': 0
    }
    
    problematic_responses = []
    
    for result in korean_results:
        response_text = result['생성된_응답']
        issues = []
        
        # Check for apology overuse
        if response_text.count('죄송합니다') > 1:
            issues.append("❌ '죄송합니다' 과다사용")
            issue_counts['apology_overuse'] += 1
        
        # Check for observational tone
        observational_patterns = ['군요', '네요', '으시네요', '는군요', '했군요', '하시는군요', '하셨네요', '이네요']
        if any(pattern in response_text for pattern in observational_patterns):
            issues.append("❌ 관찰적 어투 사용")
            issue_counts['observational_tone'] += 1
        
        # Check for emotion prediction
        emotion_patterns = ['화가 나셨을', '답답하셨겠', '실망스러우셨겠']
        if any(pattern in response_text for pattern in emotion_patterns):
            issues.append("❌ 감정 예측 사용")
            issue_counts['emotion_prediction'] += 1
        
        # Check for proper greeting
        if not response_text.startswith(('안녕하세요, 머니워크입니다', '안녕하세요, 머니워크 운영팀입니다')):
            issues.append("❌ 시작 인사 누락")
            issue_counts['missing_greeting'] += 1
        
        if issues:
            problematic_responses.append({
                'id': result['ID'],
                'original': result['원본_리뷰'][:50] + '...',
                'response': response_text[:100] + '...',
                'issues': issues
            })
    
    # Print summary
    print(f"📊 Total Korean reviews: {total_korean}")
    print(f"✅ Clean responses: {total_korean - len(problematic_responses)}")
    print(f"⚠️ Responses with issues: {len(problematic_responses)}")
    print()
    
    print("📈 Issue breakdown:")
    print(f"   '죄송합니다' 과다사용: {issue_counts['apology_overuse']}")
    print(f"   관찰적 어투: {issue_counts['observational_tone']}")
    print(f"   감정 예측: {issue_counts['emotion_prediction']}")
    print(f"   시작 인사 누락: {issue_counts['missing_greeting']}")
    print()
    
    # Show problematic responses
    if problematic_responses:
        print("🚨 Problematic responses:")
        for i, prob in enumerate(problematic_responses[:3]):  # Show first 3
            print(f"\n{i+1}. ID: {prob['id']}")
            print(f"   Original: {prob['original']}")
            print(f"   Response: {prob['response']}")
            print(f"   Issues: {', '.join(prob['issues'])}")
    else:
        print("🎉 No problematic responses found!")

if __name__ == "__main__":
    print("🚀 Processing all 42 reviews with final improved Korean prompt...")
    
    # Initialize services
    vector_store_service = VectorStoreService()
    response_generator = ResponseGenerator(vector_store_service)
    
    # Read the original CSV
    df = pd.read_csv('/Users/gravitylabs/Desktop/review/Review.csv')
    print(f"📊 Found {len(df)} reviews to process")
    
    # Split into batches of 8 to avoid timeout
    batch_size = 8
    all_results = []
    
    for i in range(0, len(df), batch_size):
        batch_num = (i // batch_size) + 1
        batch_df = df.iloc[i:i+batch_size]
        
        print(f"\n🔄 Processing Batch {batch_num} ({len(batch_df)} reviews)...")
        batch_results = process_batch(batch_df, batch_num, response_generator)
        all_results.extend(batch_results)
        
        print(f"✅ Batch {batch_num} completed ({len(batch_results)} results)")
    
    # Save final results
    output_filename = f'/Users/gravitylabs/Desktop/review/final_42_reviews_IMPROVED_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    save_with_pipe_delimiter(all_results, output_filename)
    
    print(f"\n🎉 All processing completed!")
    print(f"📊 Total reviews processed: {len(all_results)}")
    print(f"💾 Results saved to: {output_filename}")
    
    # Analyze Korean response quality
    analyze_korean_responses(all_results)
    
    # Show sample results
    print("\n=== 📝 Sample Results ===")
    for i, result in enumerate(all_results[:3]):
        print(f"\n{i+1}. ID: {result['ID']} ({result['언어']})")
        print(f"   Original: {result['원본_리뷰'][:60]}...")
        print(f"   Response: {result['생성된_응답'][:80]}...")
        print(f"   Category: {result['카테고리']}")